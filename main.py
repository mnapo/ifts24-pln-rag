import logging

from fastapi import FastAPI, HTTPException
from openai import APIConnectionError, APIStatusError, AsyncOpenAI, RateLimitError

from app.config import get_settings
from app.core.prompt_builder import build_business_instructions
from app.models.chat import ChatRequest, ChatResponse

logger = logging.getLogger(__name__)

app = FastAPI(
    title="PLN RAG",
    description="Asistente conversacional configurable para un negocio.",
    version="0.1.0",
)


@app.get("/", tags=["estado"])
async def home() -> dict[str, str]:
    return {
        "nombre": "PLN RAG",
        "estado": "activo",
        "documentacion": "/docs",
    }


@app.get("/health", tags=["estado"])
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/chat", response_model=ChatResponse, tags=["chat"])
async def chat(payload: ChatRequest) -> ChatResponse:
    settings = get_settings()
    messages = payload.messages

    if len(messages) > settings.max_history_messages:
        raise HTTPException(
            status_code=422,
            detail="El historial supera el límite permitido.",
        )
    if any(len(message.content) > settings.max_message_length for message in messages):
        raise HTTPException(
            status_code=422,
            detail="Uno de los mensajes supera el límite permitido.",
        )
    if messages[-1].role != "user":
        raise HTTPException(
            status_code=422,
            detail="El último mensaje debe ser del usuario.",
        )
    if not settings.openai_api_key:
        raise HTTPException(
            status_code=503,
            detail="El servicio de chat no está configurado: falta OPENAI_API_KEY.",
        )

    try:
        async with AsyncOpenAI(api_key=settings.openai_api_key) as client:
            response = await client.responses.create(
                model=settings.openai_model,
                instructions=build_business_instructions(settings),
                input=[message.model_dump() for message in messages],
            )
        answer = response.output_text.strip()
        if not answer:
            raise HTTPException(
                status_code=502,
                detail="El modelo no devolvió una respuesta de texto.",
            )
        return ChatResponse(message=answer)
    except HTTPException:
        raise
    except RateLimitError as exc:
        raise HTTPException(
            status_code=429,
            detail="Se alcanzó el límite de uso de OpenAI. Intenta nuevamente más tarde.",
        ) from exc
    except APIConnectionError as exc:
        logger.exception("No se pudo conectar con OpenAI.")
        raise HTTPException(
            status_code=502,
            detail="No se pudo conectar con OpenAI.",
        ) from exc
    except APIStatusError as exc:
        logger.exception("OpenAI devolvió un error.")
        raise HTTPException(
            status_code=502,
            detail="OpenAI devolvió un error al procesar el mensaje.",
        ) from exc

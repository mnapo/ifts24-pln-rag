import logging
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from openai import APIConnectionError, APIStatusError, AsyncOpenAI, RateLimitError

from app.config import get_settings
from app.core.prompt_builder import build_business_instructions
from app.models.chat import ChatRequest, ChatResponse

logger = logging.getLogger(__name__)
STATIC_DIR = Path(__file__).parent / "app" / "static"

PROVIDER_BASE_URLS = {
    "gemini": "https://generativelanguage.googleapis.com/v1beta/openai/",
    "deepseek": "https://api.deepseek.com",
    "groq": "https://api.groq.com/openai/v1",
    "openrouter": "https://openrouter.ai/api/v1",
    "openai": "https://api.openai.com/v1",
}

app = FastAPI(
    title="PLN RAG",
    description="Asistente conversacional configurable para un negocio.",
    version="0.1.0",
)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", include_in_schema=False)
async def home() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health", tags=["estado"])
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/chat", response_model=ChatResponse, tags=["chat"])
async def chat(payload: ChatRequest) -> ChatResponse:
    settings = get_settings()
    messages = payload.messages
    provider = settings.ai_provider

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
    if provider not in PROVIDER_BASE_URLS and not settings.ai_base_url:
        raise HTTPException(
            status_code=503,
            detail="El proveedor configurado no es compatible. Define AI_BASE_URL o elige un proveedor admitido.",
        )
    if not settings.ai_api_key:
        raise HTTPException(
            status_code=503,
            detail="El servicio de chat no está configurado: falta AI_API_KEY.",
        )

    base_url = settings.ai_base_url or PROVIDER_BASE_URLS[provider]

    try:
        async with AsyncOpenAI(
            api_key=settings.ai_api_key,
            base_url=base_url,
        ) as client:
            response = await client.chat.completions.create(
                model=settings.ai_model,
                messages=[
                    {
                        "role": "system",
                        "content": build_business_instructions(settings),
                    },
                    *[message.model_dump() for message in messages],
                ],
            )

        answer = (response.choices[0].message.content or "").strip()
        if not answer:
            raise HTTPException(
                status_code=502,
                detail=f"{provider.capitalize()} no devolvió una respuesta de texto.",
            )
        return ChatResponse(message=answer)
    except HTTPException:
        raise
    except RateLimitError as exc:
        logger.warning("%s rechazó la solicitud por límite de uso: %s", provider, exc)
        raise HTTPException(
            status_code=429,
            detail=f"{provider.capitalize()} está limitando temporalmente las solicitudes. Intenta nuevamente más tarde.",
        ) from exc
    except APIConnectionError as exc:
        logger.exception("No se pudo conectar con %s.", provider)
        raise HTTPException(
            status_code=502,
            detail=f"No se pudo conectar con {provider}.",
        ) from exc
    except APIStatusError as exc:
        logger.exception("%s devolvió un error HTTP %s.", provider, exc.status_code)
        if exc.status_code == 402:
            detail = f"La cuenta de {provider} no tiene saldo suficiente para procesar la solicitud."
            status_code = 402
        else:
            detail = f"{provider.capitalize()} devolvió un error al procesar el mensaje."
            status_code = 502
        raise HTTPException(status_code=status_code, detail=detail) from exc

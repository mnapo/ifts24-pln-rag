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


def _safe_error_detail(value: object, api_key: str) -> str:
    """Evita devolver credenciales si el proveedor las incluye accidentalmente en un error."""
    detail = str(value).strip() or "Sin descripción adicional."
    if api_key:
        detail = detail.replace(api_key, "[credencial ocultada]")
    return detail[:1200]


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
        raise HTTPException(status_code=422, detail="El historial supera el límite permitido.")
    if any(len(message.content) > settings.max_message_length for message in messages):
        raise HTTPException(status_code=422, detail="Uno de los mensajes supera el límite permitido.")
    if messages[-1].role != "user":
        raise HTTPException(status_code=422, detail="El último mensaje debe ser del usuario.")
    if provider not in PROVIDER_BASE_URLS and not settings.ai_base_url:
        raise HTTPException(
            status_code=503,
            detail="Proveedor no compatible. Configura AI_BASE_URL o elige un proveedor admitido.",
        )
    if not settings.ai_api_key:
        raise HTTPException(status_code=503, detail="Falta configurar AI_API_KEY.")

    base_url = settings.ai_base_url or PROVIDER_BASE_URLS[provider]

    try:
        async with AsyncOpenAI(
            api_key=settings.ai_api_key,
            base_url=base_url,
            timeout=20.0,
            max_retries=0,
        ) as client:
            response = await client.chat.completions.create(
                model=settings.ai_model,
                messages=[
                    {"role": "system", "content": build_business_instructions(settings)},
                    *[message.model_dump() for message in messages],
                ],
            )

        answer = (response.choices[0].message.content or "").strip()
        if not answer:
            raise HTTPException(
                status_code=502,
                detail=f"{provider}: el modelo devolvió una respuesta vacía.",
            )
        return ChatResponse(message=answer)
    except HTTPException:
        raise
    except RateLimitError as exc:
        logger.exception("%s respondió con límite de uso.", provider)
        raise HTTPException(
            status_code=429,
            detail=f"Error de {provider} (HTTP 429): {_safe_error_detail(exc, settings.ai_api_key)}",
        ) from exc
    except APIConnectionError as exc:
        logger.exception("Error de conexión con %s.", provider)
        raise HTTPException(
            status_code=502,
            detail=f"Error de conexión con {provider}: {_safe_error_detail(exc, settings.ai_api_key)}",
        ) from exc
    except APIStatusError as exc:
        logger.exception("%s devolvió HTTP %s.", provider, exc.status_code)
        body = exc.body if isinstance(exc.body, dict) else {}
        provider_error = body.get("error", body)
        if isinstance(provider_error, dict):
            code = provider_error.get("code") or provider_error.get("type")
            message = provider_error.get("message") or str(exc)
            diagnostic = f"{message}" + (f" (código: {code})" if code else "")
        else:
            diagnostic = str(exc)
        request_id = exc.response.headers.get("x-request-id")
        suffix = f" | ID: {request_id}" if request_id else ""
        raise HTTPException(
            status_code=exc.status_code if 400 <= exc.status_code < 600 else 502,
            detail=f"Error de {provider} (HTTP {exc.status_code}): {_safe_error_detail(diagnostic, settings.ai_api_key)}{suffix}",
        ) from exc
    except Exception as exc:
        logger.exception("Error interno al procesar una solicitud de chat.")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno ({type(exc).__name__}): {_safe_error_detail(exc, settings.ai_api_key)}",
        ) from exc

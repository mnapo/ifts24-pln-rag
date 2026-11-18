import logging
import os
from dataclasses import dataclass
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


def _env_text(name: str, default: str = "") -> str:
    """Lee una variable de entorno y aplica un valor predeterminado si falta o está vacía."""
    return os.getenv(name, default).strip() or default


def _env_int(name: str, default: int, minimum: int) -> int:
    """Convierte una variable numérica sin interrumpir el inicio ante valores inválidos."""
    raw_value = os.getenv(name, "").strip()
    if not raw_value:
        return default

    try:
        value = int(raw_value)
    except ValueError:
        logger.warning(
            "La variable %s debe ser un entero; se utilizará el valor predeterminado (%s).",
            name,
            default,
        )
        return default

    if value < minimum:
        logger.warning(
            "La variable %s debe ser mayor o igual a %s; se utilizará el valor predeterminado (%s).",
            name,
            minimum,
            default,
        )
        return default

    return value


@dataclass(frozen=True)
class Settings:
    ai_provider: str
    ai_api_key: str
    ai_model: str
    ai_base_url: str
    business_name: str
    business_sector: str
    business_description: str
    business_products: str
    business_tone: str
    business_policies: str
    business_hours: str
    business_contact: str
    business_instructions: str
    max_history_messages: int
    max_message_length: int


@lru_cache
def get_settings() -> Settings:
    """Carga la configuración con valores seguros; las credenciales se validan al usarlas."""
    return Settings(
        ai_provider=_env_text("AI_PROVIDER", "gemini").lower(),
        ai_api_key=_env_text("AI_API_KEY"),
        ai_model=_env_text("AI_MODEL", "gemini-3.8-flash"),
        ai_base_url=_env_text("AI_BASE_URL").rstrip("/"),
        business_name=_env_text("BUSINESS_NAME", "Mi negocio"),
        business_sector=_env_text("BUSINESS_SECTOR", "No especificado"),
        business_description=_env_text("BUSINESS_DESCRIPTION"),
        business_products=_env_text("BUSINESS_PRODUCTS"),
        business_tone=_env_text("BUSINESS_TONE", "Claro, cordial y profesional"),
        business_policies=_env_text("BUSINESS_POLICIES"),
        business_hours=_env_text("BUSINESS_HOURS"),
        business_contact=_env_text("BUSINESS_CONTACT"),
        business_instructions=_env_text("BUSINESS_INSTRUCTIONS"),
        max_history_messages=_env_int("MAX_HISTORY_MESSAGES", 30, 2),
        max_message_length=_env_int("MAX_MESSAGE_LENGTH", 4000, 100),
    )

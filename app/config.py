from dataclasses import dataclass
from functools import lru_cache
import os

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    openai_api_key: str
    openai_model: str
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
    return Settings(
        openai_api_key=os.getenv("OPENAI_API_KEY", "").strip(),
        openai_model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini").strip(),
        business_name=os.getenv("BUSINESS_NAME", "Mi negocio").strip(),
        business_sector=os.getenv("BUSINESS_SECTOR", "").strip(),
        business_description=os.getenv("BUSINESS_DESCRIPTION", "").strip(),
        business_products=os.getenv("BUSINESS_PRODUCTS", "").strip(),
        business_tone=os.getenv("BUSINESS_TONE", "Claro, cordial y profesional").strip(),
        business_policies=os.getenv("BUSINESS_POLICIES", "").strip(),
        business_hours=os.getenv("BUSINESS_HOURS", "").strip(),
        business_contact=os.getenv("BUSINESS_CONTACT", "").strip(),
        business_instructions=os.getenv("BUSINESS_INSTRUCTIONS", "").strip(),
        max_history_messages=max(2, int(os.getenv("MAX_HISTORY_MESSAGES", "30"))),
        max_message_length=max(100, int(os.getenv("MAX_MESSAGE_LENGTH", "4000"))),
    )

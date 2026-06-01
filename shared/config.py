import os
from dotenv import load_dotenv

load_dotenv()

def get(key: str, default: str = "") -> str:
    """Pobiera parametr konfiguracyjny ze zmiennych środowiskowych."""
    return os.getenv(key, default)

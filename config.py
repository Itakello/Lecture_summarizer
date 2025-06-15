import os
from pathlib import Path
from dotenv import load_dotenv

# Load variables from a local .env if present
load_dotenv()

# ---------------------------------------------------------------------------
#  Core configuration constants pulled from the environment
# ---------------------------------------------------------------------------
LANGUAGE: str = os.getenv("LANGUAGE", "ENG").upper()  # ENG | ITA
OWNER: str | None = os.getenv("OWNER")

# Notion integration
NOTION_DB_ID: str | None = os.getenv("NOTION_DB_ID")
NOTION_API_KEY: str | None = os.getenv("NOTION_API_KEY")

# OpenAI
OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o")
TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.1"))

# Paths
PROMPTS_PATH: Path = Path("prompts")

# ---------------------------------------------------------------------------
#  Validation helpers
# ---------------------------------------------------------------------------

def validate() -> None:
    """Validate mandatory configuration values and raise if they're missing."""
    if LANGUAGE not in {"ENG", "ITA"}:
        raise EnvironmentError("LANGUAGE must be ENG or ITA")
    if OPENAI_API_KEY is None:
        raise EnvironmentError("OPENAI_API_KEY is missing")
    if NOTION_DB_ID is None or NOTION_API_KEY is None:
        raise EnvironmentError("NOTION_DB_ID and NOTION_API_KEY must be set")


def output_language() -> str:
    """Return the full language string expected by LLM prompts."""
    return "English" if LANGUAGE == "ENG" else "Italian"

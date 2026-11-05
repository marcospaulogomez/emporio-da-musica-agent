import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Ensure UTF-8 output on Windows terminals
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Load environment variables from .env file (override=True reloads changes)
load_dotenv(override=True)

# Base project directories
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

# OpenAI & Gemini API Configuration (supports both providers seamlessly)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip()


def resolve_data_file(clean_name: str, fallback_candidates: list[str]) -> Path:
    """
    Locates a data file inside the data/ directory, accepting both
    clean names and original challenge filenames (with prefixes or accents).
    """
    primary_path = DATA_DIR / clean_name
    if primary_path.exists():
        return primary_path

    for candidate in fallback_candidates:
        candidate_path = DATA_DIR / candidate
        if candidate_path.exists():
            return candidate_path

    raise FileNotFoundError(
        f"Data file '{clean_name}' not found in {DATA_DIR}. "
        f"Please verify that all operational files are placed inside the data/ folder."
    )

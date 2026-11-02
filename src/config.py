import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base project directories
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

# Gemini API Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")


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
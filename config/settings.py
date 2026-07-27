import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
VECTOR_DB_DIR = BASE_DIR / "vectordb"
LOG_DIR = BASE_DIR / "logs"
CACHE_DIR = BASE_DIR / "cache"

# Ensure runtime directories exist
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(CACHE_DIR, exist_ok=True)
os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)

# Database Config
VECTOR_DB_TYPE = os.getenv("VECTOR_DB_TYPE", "chroma")
CHROMA_PERSIST_DIR = VECTOR_DB_DIR / "chroma"
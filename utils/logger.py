import logging
import sys
from pathlib import Path

# Create logs directory if it doesn't exist
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

# Configure the global logging format
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "rag_system.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout) # Prints to terminal as well
    ]
)

def get_logger(name: str):
    """Returns a configured logger instance for the given module name."""
    return logging.getLogger(name)
import logging
import os
from dotenv import load_dotenv

load_dotenv()

LOG_LEVEL = logging.DEBUG if os.getenv("APP_ENV") == "development" else logging.INFO

logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)

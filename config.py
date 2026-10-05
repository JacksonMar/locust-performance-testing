import os
from pathlib import Path




ROOT_DIR = Path(__file__).resolve().parent
DATA_DIR = ROOT_DIR / "perf" / "data"
HOST = os.getenv("HOST", "https://fragstore.ua")
USER_AGENT = {"User-Agent": os.getenv(
    "USER_AGENT",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
)}
ITEMS_PER_PAGE = int(os.getenv("ITEMS_PER_PAGE", 80))
TIMEOUT = 10
import os
from pathlib import Path




ROOT_DIR = Path(__file__).resolve().parent
DATA_DIR = ROOT_DIR / "perf" / "data"
HOST = os.getenv("HOST", "https://fragstore.ua")
USER_AGENT =  {"User-Agent": "Mozilla/5.0 ... Chrome/140.0 Safari/537.36"}
ITEMS_PER_PAGE = int(os.getenv("ITEMS_PER_PAGE", 80))
TIMEOUT = 10
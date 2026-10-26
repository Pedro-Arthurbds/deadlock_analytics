import json
from pathlib import Path
from config import RAW_DATA_DIR, ENDPOINT_ITEMS, logger
from ingestion.client import DeadlockAPIClient

ITEMS_CACHE_FILE = RAW_DATA_DIR / "items.json"
client = DeadlockAPIClient()

def fetch_items_assets(use_cache: bool = True) -> list[dict]:
    """Coleta o catálogo de itens da API Deadlock com suporte a cache local."""
    if use_cache and ITEMS_CACHE_FILE.exists():
        logger.info("Carregando itens do cache local: %s", ITEMS_CACHE_FILE)
        with open(ITEMS_CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    # Fora do if (4 espaços):
    logger.info("Buscando catálogo de itens na API Deadlock...")
    data = client.get(ENDPOINT_ITEMS)

    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(ITEMS_CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    logger.info("✅ %d itens salvos em cache local.", len(data))
    return data
import json
from pathlib import Path
from config import RAW_DATA_DIR, ENDPOINT_HEROES, ENDPOINT_HERO_STATS, logger
from ingestion.client import DeadlockAPIClient

HEROES_CACHE_FILE = RAW_DATA_DIR / "heroes.json"
HERO_STATS_CACHE_FILE = RAW_DATA_DIR / "hero_stats.json"

client = DeadlockAPIClient()


def fetch_heroes_assets(use_cache: bool = True) -> list[dict]:
    """Coleta dados cadastrais (assets) dos heróis com cache local."""
    if use_cache and HEROES_CACHE_FILE.exists():
        logger.info("Carregando heróis do cache: %s", HEROES_CACHE_FILE)
        with open(HEROES_CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    logger.info("Buscando heróis na API Deadlock...")
    data = client.get(ENDPOINT_HEROES)

    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(HEROES_CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    logger.info("✅ %d heróis salvos em cache.", len(data))
    return data


def fetch_heroes_stats(use_cache: bool = True) -> list[dict]:
    """Coleta estatísticas agregadas dos heróis com cache local."""
    if use_cache and HERO_STATS_CACHE_FILE.exists():
        logger.info("Carregando estatísticas do cache: %s", HERO_STATS_CACHE_FILE)
        with open(HERO_STATS_CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    logger.info("Buscando estatísticas na API Deadlock...")
    data = client.get(ENDPOINT_HERO_STATS)

    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(HERO_STATS_CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    logger.info("✅ Estatísticas salvas em cache.")
    return data


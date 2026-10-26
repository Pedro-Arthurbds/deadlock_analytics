import time
import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent.parent
if str(SRC_DIR) not in sys.path:
    sys.path.append(str(SRC_DIR))

from config import logger
from database import test_connection, save_df_to_db
# 1. Importamos os coletores
from ingestion import fetch_heroes_assets, fetch_heroes_stats, fetch_items_assets
# 2. Importamos as transformações
from transformations import (
    transform_heroes_dimension,
    transform_hero_stats_fact,
    transform_items_dimension,
    transform_hero_build_items,
)


def run_full_pipeline(use_cache: bool = True) -> bool:
    """Executa o pipeline completo: Ingestão -> Transformação -> Persistência."""
    start_time = time.time()
    logger.info("🚀 INICIANDO O PIPELINE COMPLETO DO DEADLOCK ANALYTICS")

    if not test_connection():
        logger.error("❌ Abortando pipeline: Falha na conexão com o PostgreSQL.")
        return False

    try:
        # ETAPA 1: Ingestão de Dados Brutos (Extract)
        logger.info("--- ETAPA 1: Ingestão de Dados Brutos ---")
        raw_heroes = fetch_heroes_assets(use_cache=use_cache)
        raw_stats = fetch_heroes_stats(use_cache=use_cache)
        raw_items = fetch_items_assets(use_cache=use_cache)  # <-- NOVO!

        # ETAPA 2: Transformação com Pandas (Transform)
        logger.info("--- ETAPA 2: Transformação e Regras de Negócio ---")
        df_dim_heroes = transform_heroes_dimension(raw_heroes)
        df_fact_hero_stats = transform_hero_stats_fact(raw_stats)
        df_dim_items = transform_items_dimension(raw_items)
        df_fact_builds = transform_hero_build_items(raw_heroes)

        # ETAPA 3: Persistência no PostgreSQL (Load)
        logger.info("--- ETAPA 3: Persistência no PostgreSQL ---")
        save_df_to_db(df_dim_heroes, table_name="dim_heroes")
        save_df_to_db(df_fact_hero_stats, table_name="fact_hero_stats")
        save_df_to_db(df_dim_items, table_name="dim_items")
        save_df_to_db(df_fact_builds, table_name="fact_hero_build_items")

        elapsed = time.time() - start_time
        logger.info("🎉 PIPELINE FINALIZADO COM SUCESSO EM %.2f SEGUNDOS!", elapsed)
        return True

    except Exception as e:
        logger.exception("❌ Falha crítica durante a execução do pipeline: %s", e)
        return False


if __name__ == "__main__":
    run_full_pipeline()
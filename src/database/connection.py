import time
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool
from config import DATABASE_URL, logger

# Cria a engine reutilizável conectando via URL centralizada no config.
# Com bancos serverless (Neon com pooler PgBouncer), NullPool evita que conexões fiquem
# ociosas na memória do Streamlit enquanto o banco entra em hibernação (Scale-to-zero).
engine = create_engine(
    DATABASE_URL,
    poolclass=NullPool,
    connect_args={"connect_timeout": 15},
)


def read_sql_with_retry(query: str, max_retries: int = 3, delay: float = 1.5) -> pd.DataFrame:
    """Executa uma query SQL com tentativas automáticas em caso de desconexão (útil para cold start do Neon)."""
    last_error = None
    for attempt in range(max_retries):
        try:
            with engine.connect() as connection:
                return pd.read_sql(text(query), con=connection)
        except Exception as e:
            last_error = e
            if attempt < max_retries - 1:
                logger.warning(
                    "Tentativa %d/%d falhou ao consultar banco (%s). Reconectando em %.1fs...",
                    attempt + 1, max_retries, e, delay
                )
                time.sleep(delay)
            else:
                logger.error("Todas as %d tentativas falharam: %s", max_retries, e)
                raise last_error


def test_connection() -> bool:
    """Testa a comunicação com o PostgreSQL e registra nos logs."""
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT version();"))
            db_version = result.fetchone()[0]
            logger.info("Conexão com PostgreSQL bem-sucedida! Versão: %s", db_version)
            return True
    except Exception as e:
        logger.error("Erro ao conectar com PostgreSQL: %s", e)
        return False


def save_df_to_db(df: pd.DataFrame, table_name: str, if_exists: str = "replace") -> bool:
    """Salva qualquer DataFrame do Pandas no PostgreSQL de forma genérica."""
    try:
        df.to_sql(name=table_name, con=engine, if_exists=if_exists, index=False)
        logger.info("✅ %d registros salvos na tabela '%s' do PostgreSQL!", len(df), table_name)
        return True
    except Exception as e:
        logger.error("❌ Erro ao salvar na tabela '%s': %s", table_name, e)
        return False


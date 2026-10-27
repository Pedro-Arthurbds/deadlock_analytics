import pandas as pd
from sqlalchemy import create_engine, text
from config import DATABASE_URL, logger

# Cria a engine reutilizável conectando via URL centralizada no config.
# pool_pre_ping=True: testa a conexão antes de usar (essencial para bancos serverless como Neon que hibernam)
# pool_recycle=300: recicla conexões a cada 5 minutos para evitar conexões presas ou expiradas
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
)


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


import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import pandas as pd

# 1. Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "deadlock_db")

# 2. Monta a URL de conexão do PostgreSQL
DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# 3. Cria a Engine do SQLAlchemy
engine = create_engine(DATABASE_URL)


def test_connection():
    """Testa se o Python consegue se comunicar com o PostgreSQL."""
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT version();"))
            db_version = result.fetchone()[0]
            print(" Conexão com o PostgreSQL realizada com sucesso!")
            print(f"-> Versão do Banco: {db_version}")
            return True
    except Exception as e:
        print("❌ Erro ao conectar com o PostgreSQL:")
        print(e)
        return False


def save_heroes_to_db(df, table_name="dim_heroes"):
    """Salva o DataFrame de heróis na tabela do PostgreSQL."""
    try:
        # if_exists="replace" recria a tabela com os dados atualizados
        df.to_sql(name=table_name, con=engine, if_exists="replace", index=False)
        print(f"✅ {len(df)} heróis salvos com sucesso na tabela '{table_name}' do PostgreSQL!")
    except Exception as e:
        print(f"❌ Erro ao salvar heróis no banco: {e}")


def get_active_heroes_from_db():
    """Consulta apenas os heróis ativos diretamente do PostgreSQL via SQL."""
    query = """
        SELECT hero_id, name, hero_type, is_active
        FROM dim_heroes
        WHERE is_active = TRUE
        ORDER BY name ASC;
    """
    with engine.connect() as conn:
        df = pd.read_sql(query, con=conn)
        return df


if __name__ == "__main__":
    test_connection()


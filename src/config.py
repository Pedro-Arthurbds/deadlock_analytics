import logging
import os
from pathlib import Path
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# --- Diretórios do Projeto ---
PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "data"
RAW_DATA_DIR = DATA_DIR

# --- Endpoints da API Deadlock ---
BASE_URL = "https://api.deadlock-api.com"
ENDPOINT_HEROES = "/v1/assets/heroes"
ENDPOINT_HERO_STATS = "/v1/analytics/hero-stats"
ENDPOINT_ITEMS = "/v1/assets/items"

# --- Configurações do PostgreSQL ---
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "deadlock_db")

DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# --- Configuração Padronizada de Logs ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("DeadlockAnalytics")


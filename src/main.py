import json
from pathlib import Path
import pandas as pd
import requests
from database import save_heroes_to_db

# --- Configurações e Constantes ---
BASE_URL = "https://api.deadlock-api.com"
ENDPOINT = "/v1/assets/heroes"

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "data"
OUTPUT_FILE = DATA_DIR / "heroes.json"


# --- 1. Camada de Ingestão (Coleta e Armazenamento Bruto) ---
def fetch_heroes() -> list[dict]:
    """Faz a requisição HTTP para a API do Deadlock e retorna a lista bruta de heróis."""
    url = f"{BASE_URL}{ENDPOINT}"
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response.json()


def save_heroes(heroes: list[dict]) -> None:
    """Salva os dados brutos em formato JSON no disco (cache local)."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with OUTPUT_FILE.open("w", encoding="utf-8") as file:
        json.dump(heroes, file, ensure_ascii=False, indent=2)


def load_heroes() -> list[dict]:
    """Carrega os dados brutos do arquivo JSON local."""
    with OUTPUT_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


# --- 2. Camada de Transformação (Limpeza e Modelagem) ---
def transform_heroes(raw_heroes: list[dict]) -> pd.DataFrame:
    """
    Transforma a lista de dicionários brutos da API em um DataFrame tabular
    estruturado para a tabela dimensional (dim_heroes).
    """
    processed_heroes = []

    for hero in raw_heroes:
        # Regra de negócio: Herói ativo precisa ser selecionável e não desativado
        is_selectable = hero.get("player_selectable", False)
        is_disabled = hero.get("disabled", False)
        is_active = is_selectable and not is_disabled

        hero_data = {
            "hero_id": hero.get("id"),
            "name": hero.get("name"),
            "class_name": hero.get("class_name"),
            "hero_type": hero.get("hero_type"),
            "is_active": is_active,
            "in_development": hero.get("in_development", False),
            "image_url": hero.get("images", {}).get("icon_image_small_webp"),
        }
        processed_heroes.append(hero_data)

    df = pd.DataFrame(processed_heroes)
    return df


# --- 3. Execução Principal ---
def main():
    print("=== Pipeline de Ingestão e Transformação de Heróis ===")

    # 1. Coleta ou Carregamento (Cache)
    if OUTPUT_FILE.exists():
        print("-> Arquivo bruto encontrado em cache. Carregando dados locais...")
        raw_heroes = load_heroes()
    else:
        print("-> Cache não encontrado. Buscando heróis na API...")
        raw_heroes = fetch_heroes()
        save_heroes(raw_heroes)
        print("-> Dados brutos salvos com sucesso!")

    print(f"Total de heróis brutos carregados: {len(raw_heroes)}")

    # 2. Transformação com Pandas
    print("\n-> Transformando dados com Pandas...")
    df_heroes = transform_heroes(raw_heroes)

    # 3. Visualização e Auditoria dos Dados
    print("\n--- Primeiros 5 heróis transformados ---")
    print(df_heroes.head())

    print("\n--- Contagem: Heróis Ativos vs Descontinuados ---")
    print(df_heroes["is_active"].value_counts())

    # 4. Persistência no Banco de Dados
    print("\n-> Persistindo dados no PostgreSQL...")
    save_heroes_to_db(df_heroes)


if __name__ == "__main__":
    main()

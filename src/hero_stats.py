import json
from pathlib import Path
import pandas as pd
import requests
from database import engine

# --- Configurações ---
BASE_URL = "https://api.deadlock-api.com"
ENDPOINT = "/v1/analytics/hero-stats"

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "data"
OUTPUT_FILE = DATA_DIR / "hero_stats.json"


def fetch_hero_stats() -> list[dict]:
    """Coleta as estatísticas agregadas dos heróis na API."""
    url = f"{BASE_URL}{ENDPOINT}"
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response.json()


def save_raw_stats(stats: list[dict]) -> None:
    """Salva a resposta bruta em JSON (cache local)."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with OUTPUT_FILE.open("w", encoding="utf-8") as file:
        json.dump(stats, file, ensure_ascii=False, indent=2)


def load_raw_stats() -> list[dict]:
    """Carrega as estatísticas brutas do cache local."""
    with OUTPUT_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def transform_hero_stats(raw_stats: list[dict]) -> pd.DataFrame:
    """Extrai e calcula as métricas analíticas reais a partir dos totais brutos."""
    processed = []

    # Em Deadlock são 12 heróis por partida (6v6). 
    # Somamos todas as participações de heróis para calcular o pick rate relativo.
    total_hero_picks = sum(item.get("matches", 0) for item in raw_stats)
    total_matches_estimated = (total_hero_picks / 12) if total_hero_picks > 0 else 1

    for item in raw_stats:
        matches = item.get("matches", 0)
        wins = item.get("wins", 0)

        # 1. Taxa de Vitória (Win Rate %)
        win_rate = (wins / matches * 100) if matches > 0 else 0.0

        # 2. Taxa de Escolha (Pick Rate %)
        pick_rate = (matches / total_matches_estimated * 100) if total_matches_estimated > 0 else 0.0

        # 3. Médias por partida (Kills, Deaths, Assists, Net Worth)
        avg_kills = (item.get("total_kills", 0) / matches) if matches > 0 else 0.0
        avg_deaths = (item.get("total_deaths", 0) / matches) if matches > 0 else 0.0
        avg_assists = (item.get("total_assists", 0) / matches) if matches > 0 else 0.0
        avg_net_worth = (item.get("total_net_worth", 0) / matches) if matches > 0 else 0.0

        processed.append({
            "hero_id": item.get("hero_id"),
            "matches": matches,
            "wins": wins,
            "win_rate": round(win_rate, 2),
            "pick_rate": round(pick_rate, 2),
            "avg_kills": round(avg_kills, 2),
            "avg_deaths": round(avg_deaths, 2),
            "avg_assists": round(avg_assists, 2),
            "avg_net_worth": round(avg_net_worth, 0),
        })

    return pd.DataFrame(processed)


def save_stats_to_db(df: pd.DataFrame, table_name="fact_hero_stats") -> None:
    """Persiste a tabela de fatos no PostgreSQL."""
    try:
        df.to_sql(name=table_name, con=engine, if_exists="replace", index=False)
        print(f"✅ {len(df)} registros salvos com sucesso na tabela '{table_name}'!")
    except Exception as e:
        print(f"❌ Erro ao salvar estatísticas no banco: {e}")


def query_meta_ranking() -> pd.DataFrame:
    """
    Executa a consulta analítica cruzando a Dimensão (dim_heroes)
    com a Tabela de Fatos (fact_hero_stats) via INNER JOIN no PostgreSQL.
    """
    query = """
        SELECT 
            d.hero_id,
            d.name AS heroi,
            d.hero_type AS tipo,
            f.matches AS partidas,
            f.win_rate AS win_rate_pct,
            f.pick_rate AS pick_rate_pct,
            f.avg_kills AS abates_medios,
            f.avg_deaths AS mortes_medias,
            f.avg_assists AS assist_medias
        FROM fact_hero_stats f
        INNER JOIN dim_heroes d ON f.hero_id = d.hero_id
        WHERE d.is_active = TRUE
        ORDER BY f.win_rate DESC;
    """
    with engine.connect() as conn:
        df_ranking = pd.read_sql(query, con=conn)
        return df_ranking


def main():
    print("=== Pipeline de Estatísticas de Heróis (Fact Table) ===")

    # 1. Coleta / Cache
    if OUTPUT_FILE.exists():
        print("-> Cache encontrado. Carregando 'hero_stats.json'...")
        raw_stats = load_raw_stats()
    else:
        print("-> Coletando estatísticas da API...")
        raw_stats = fetch_hero_stats()
        save_raw_stats(raw_stats)
        print("-> Dados brutos salvos em cache.")

    # 2. Transformação
    df_stats = transform_hero_stats(raw_stats)
    print("\n--- Amostra das Estatísticas Transformadas ---")
    print(df_stats.head())

    # 3. Persistência no PostgreSQL
    save_stats_to_db(df_stats)

    # 4. Consulta Analítica: O SQL JOIN
    print("\n================== TOP 10 HERÓIS DO META ==================")
    print("Cruzando 'dim_heroes' (dimensão) com 'fact_hero_stats' (fatos) via SQL:\n")
    df_ranking = query_meta_ranking()
    print(df_ranking.head(10).to_string(index=False))


if __name__ == "__main__":
    main()


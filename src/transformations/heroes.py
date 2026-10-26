import pandas as pd
from config import logger


def transform_heroes_dimension(raw_heroes: list[dict]) -> pd.DataFrame:
    """
    Transforma dados brutos dos heróis na Dimensão dim_heroes,
    aplicando a regra de heróis ativos vs descontinuados.
    """
    processed = []

    for hero in raw_heroes:
        is_selectable = hero.get("player_selectable", False)
        is_disabled = hero.get("disabled", False)
        is_active = is_selectable and not is_disabled

        processed.append({
            "hero_id": hero.get("id"),
            "name": hero.get("name"),
            "class_name": hero.get("class_name"),
            "hero_type": hero.get("hero_type"),
            "is_active": is_active,
            "in_development": hero.get("in_development", False),
            "image_url": hero.get("images", {}).get("icon_image_small_webp"),
        })

    df = pd.DataFrame(processed)
    logger.info("Transformados %d heróis para a dimensão dim_heroes (Ativos: %d).", len(df), df["is_active"].sum())
    return df


def transform_hero_stats_fact(raw_stats: list[dict]) -> pd.DataFrame:
    """
    Transforma dados agregados brutos na Tabela de Fatos fact_hero_stats,
    calculando taxas relativas de vitória, escolha e médias de KDA.
    """
    processed = []

    # Em Deadlock são 12 heróis por partida (6v6).
    total_hero_picks = sum(item.get("matches", 0) for item in raw_stats)
    total_matches_estimated = (total_hero_picks / 12) if total_hero_picks > 0 else 1

    for item in raw_stats:
        matches = item.get("matches", 0)
        wins = item.get("wins", 0)

        win_rate = (wins / matches * 100) if matches > 0 else 0.0
        pick_rate = (matches / total_matches_estimated * 100) if total_matches_estimated > 0 else 0.0

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

    df = pd.DataFrame(processed)
    logger.info("Calculadas estatísticas para %d heróis na tabela fact_hero_stats.", len(df))
    return df


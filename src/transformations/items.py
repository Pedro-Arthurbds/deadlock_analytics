import re
import pandas as pd
from config import logger


def clean_html(text: str) -> str:
    """Remove tags HTML como <span> e <br> da descrição."""
    if not text:
        return ""
    # Substitui tags por espaço e limpa espaços extras
    cleaned = re.sub(r"<[^>]+>", " ", str(text))
    return " ".join(cleaned.split())


def extract_description(desc_obj) -> str:
    """Extrai e consolida as descrições de dicionário em uma única string legível."""
    if not isinstance(desc_obj, dict):
        return clean_html(str(desc_obj or ""))

    parts = []
    if desc_obj.get("desc"):
        parts.append(clean_html(desc_obj["desc"]))
    if desc_obj.get("desc2"):
        parts.append(clean_html(desc_obj["desc2"]))
    if desc_obj.get("passive"):
        parts.append(f"Passiva: {clean_html(desc_obj['passive'])}")
    if desc_obj.get("active"):
        parts.append(f"Ativa: {clean_html(desc_obj['active'])}")

    return " | ".join(parts) if parts else ""


def infer_tier(cost: int, raw_tier: int = None) -> int:
    """Infere com precisão o Tier do item (1 a 4) com base no custo de Almas."""
    if raw_tier and str(raw_tier).isdigit() and int(raw_tier) in [1, 2, 3, 4]:
        return int(raw_tier)
    cost_val = int(cost or 500)
    if cost_val <= 800:
        return 1
    elif cost_val <= 1600:
        return 2
    elif cost_val <= 3200:
        return 3
    else:
        return 4


def transform_items_dimension(raw_items: list[dict]) -> pd.DataFrame:
    """
    Transforma dados brutos de itens na tabela dimensional dim_items.
    Filtra apenas itens válidos das 3 categorias principais do jogo (Weapon, Vitality, Spirit).
    """
    processed = []
    valid_slots = {"weapon", "vitality", "spirit"}

    for item in raw_items:
        slot_type = str(item.get("item_slot_type", "")).lower()

        # Regra de negócio: filtrar apenas upgrades válidos da loja
        if slot_type in valid_slots and item.get("name"):
            cost_val = int(item.get("cost", 500) or 500)
            tier_val = infer_tier(cost_val, item.get("tier"))

            processed.append({
                "item_id": item.get("id"),
                "name": item.get("name"),
                "class_name": item.get("class_name"),
                "slot_type": slot_type,
                "tier": tier_val,
                "cost": cost_val,
                "is_active_ability": item.get("is_active", False),
                "description": extract_description(item.get("description")),
                "image_url": item.get("image", ""),
            })

    df = pd.DataFrame(processed)
    logger.info("Transformados %d itens válidos para a dimensão dim_items.", len(df))
    return df


def transform_hero_build_items(raw_heroes: list[dict]) -> pd.DataFrame:
    """
    Extrai as estatísticas de builds e itens populares por herói
    divididos em Early Game, Mid Game e Late Game (tabela fact_hero_build_items).
    """
    records = []

    for hero in raw_heroes:
        # Considera apenas heróis jogáveis
        if not (hero.get("player_selectable") and not hero.get("disabled")):
            continue

        hero_id = hero.get("id")
        popular_items = hero.get("popular_items", {})

        for stage in ["early_game", "mid_game", "late_game"]:
            stage_items = popular_items.get(stage, [])
            for it in stage_items:
                records.append({
                    "hero_id": hero_id,
                    "game_stage": stage,
                    "item_id": it.get("item_id"),
                    "pick_pct": round(float(it.get("pick_pct", 0.0)), 2),
                    "winrate_pct": round(float(it.get("winrate_pct", 0.0)), 2),
                })

    df = pd.DataFrame(records)
    logger.info("Mapeados %d registros de builds na tabela fact_hero_build_items.", len(df))
    return df


def transform_hero_build_items(raw_heroes: list[dict]) -> pd.DataFrame:
    """
    Extrai as estatísticas de builds e itens populares por herói
    divididos em Early Game, Mid Game e Late Game (tabela fact_hero_build_items).
    """
    records = []

    for hero in raw_heroes:
        # Considera apenas heróis jogáveis
        if not (hero.get("player_selectable") and not hero.get("disabled")):
            continue

        hero_id = hero.get("id")
        popular_items = hero.get("popular_items", {})

        for stage in ["early_game", "mid_game", "late_game"]:
            stage_items = popular_items.get(stage, [])
            for it in stage_items:
                records.append({
                    "hero_id": hero_id,
                    "game_stage": stage,
                    "item_id": it.get("item_id"),
                    "pick_pct": round(float(it.get("pick_pct", 0.0)), 2),
                    "winrate_pct": round(float(it.get("winrate_pct", 0.0)), 2),
                })

    df = pd.DataFrame(records)
    logger.info("Mapeados %d registros de builds na tabela fact_hero_build_items.", len(df))
    return df

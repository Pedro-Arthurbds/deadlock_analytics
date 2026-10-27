import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR / "src"))

import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import text
from database import engine

# --- Configuração Geral da Aplicação ---
st.set_page_config(
    page_title="Deadlock Meta & Builds",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# --- CSS Gamer Inspirado no Mobalytics, Tracklock e OP.GG ---
st.markdown("""
<style>
    /* Estilo Geral Gamer Escuro */
    .stApp {
        background-color: #0d0f15;
    }
    
    /* Banner do Herói estilo Mobalytics */
    .hero-banner-card {
        background: linear-gradient(135deg, #161924 0%, #0e1017 100%);
        border: 1px solid #282e42;
        border-radius: 14px;
        padding: 22px;
        margin-bottom: 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
    }
    
    /* Badges de Tier */
    .badge-tier-s { 
        background: linear-gradient(135deg, #ffd166 0%, #f77f00 100%);
        color: #000; font-weight: 800; padding: 4px 12px; border-radius: 6px; font-size: 13px; letter-spacing: 0.5px;
    }
    .badge-tier-a { 
        background: linear-gradient(135deg, #48cae4 0%, #0077b6 100%);
        color: #fff; font-weight: 800; padding: 4px 12px; border-radius: 6px; font-size: 13px; letter-spacing: 0.5px;
    }
    .badge-tier-b { 
        background: #2b334a; color: #a0aec0; font-weight: 700; padding: 4px 10px; border-radius: 6px; font-size: 12px;
    }
    .badge-tier-c { 
        background: #1f2433; color: #718096; font-weight: 700; padding: 4px 10px; border-radius: 6px; font-size: 12px;
    }
    
    /* Chips de Categorias dos Itens */
    .slot-weapon { color: #f39c12; font-weight: 700; }
    .slot-vitality { color: #2ecc71; font-weight: 700; }
    .slot-spirit { color: #9b59b6; font-weight: 700; }
    
    .soul-chip {
        color: #ffd166;
        font-weight: 700;
        background-color: rgba(255, 209, 102, 0.1);
        border: 1px solid rgba(255, 209, 102, 0.25);
        padding: 2px 8px;
        border-radius: 5px;
        font-size: 12px;
    }
</style>
""", unsafe_allow_html=True)


def calculate_tier(win_rate: float) -> str:
    """Calcula o Tier competitivo do herói."""
    if win_rate >= 52.0:
        return "S"
    elif win_rate >= 50.0:
        return "A"
    elif win_rate >= 48.0:
        return "B"
    else:
        return "C"


def translate_type(hero_type: str) -> str:
    translations = {
        "marksman": "🎯 Atirador / DPS",
        "mystic": "🔮 Místico / Habilidades",
        "brawler": "⚔️ Lutador / Frontline",
        "Indefinido": "Outro",
    }
    return translations.get(str(hero_type).lower(), "Outro")


def translate_slot(slot: str) -> str:
    slots = {
        "weapon": "🟠 Arma",
        "vitality": "🟢 Vitalidade",
        "spirit": "🟣 Espírito",
    }
    return slots.get(str(slot).lower(), str(slot).title())


@st.cache_data(ttl=600)
def load_heroes_data() -> pd.DataFrame:
    query = """
        SELECT 
            d.hero_id,
            d.name AS heroi,
            COALESCE(d.hero_type, 'Indefinido') AS tipo_original,
            d.is_active,
            f.matches AS partidas,
            f.wins AS vitorias,
            f.win_rate,
            f.pick_rate,
            f.avg_kills,
            f.avg_deaths,
            f.avg_assists,
            f.avg_net_worth
        FROM fact_hero_stats f
        INNER JOIN dim_heroes d ON f.hero_id = d.hero_id
        WHERE d.is_active = TRUE
        ORDER BY f.win_rate DESC;
    """
    with engine.connect() as conn:
        df = pd.read_sql(text(query), con=conn)

    # Mapeia avatares dos heróis
    raw_heroes_path = ROOT_DIR / "data" / "heroes.json"
    avatar_map = {}
    if raw_heroes_path.exists():
        try:
            with open(raw_heroes_path, "r", encoding="utf-8") as f:
                heroes_json = json.load(f)
                avatar_map = {
                    h.get("id"): h.get("images", {}).get("icon_image_small_webp")
                    for h in heroes_json
                }
        except Exception:
            pass

    df["avatar"] = df["hero_id"].map(avatar_map)
    df["tipo"] = df["tipo_original"].apply(translate_type)
    df["tier"] = df["win_rate"].apply(calculate_tier)
    df["kda"] = df.apply(lambda r: f"{r['avg_kills']:.1f} / {r['avg_deaths']:.1f} / {r['avg_assists']:.1f}", axis=1)
    return df


@st.cache_data(ttl=600)
def load_items_catalog() -> pd.DataFrame:
    query = """
        SELECT 
            item_id,
            name AS item,
            slot_type,
            tier,
            cost AS custo,
            is_active_ability,
            description AS descricao,
            image_url AS imagem
        FROM dim_items
        ORDER BY tier ASC, cost ASC, name ASC;
    """
    with engine.connect() as conn:
        df = pd.read_sql(text(query), con=conn)

    df["categoria"] = df["slot_type"].apply(translate_slot)
    df["tipo_habilidade"] = df["is_active_ability"].apply(lambda a: "⚡ Ativa" if a else "Passiva")
    return df


@st.cache_data(ttl=600)
def load_hero_builds() -> pd.DataFrame:
    query = """
        SELECT 
            b.item_id,
            d.name AS heroi,
            b.game_stage,
            i.name AS item,
            i.slot_type,
            i.tier,
            i.cost AS custo,
            i.image_url AS imagem,
            i.description AS descricao,
            b.pick_pct,
            b.winrate_pct
        FROM fact_hero_build_items b
        INNER JOIN dim_heroes d ON b.hero_id = d.hero_id
        INNER JOIN dim_items i ON b.item_id = i.item_id
        ORDER BY b.game_stage, b.pick_pct DESC;
    """
    with engine.connect() as conn:
        df = pd.read_sql(text(query), con=conn)

    df["categoria"] = df["slot_type"].apply(translate_slot)
    return df


def render_mobalytics_card(item_row):
    """Renderiza um card visual de item com altura uniforme e alinhamento perfeito."""
    slot_color_map = {
        "weapon": "#f39c12",
        "vitality": "#2ecc71",
        "spirit": "#9b59b6",
    }
    slot_color = slot_color_map.get(item_row["slot_type"], "#4f5b7a")

    with st.container(border=True):
        # 1. Topo do Card: Imagem + Nome + Categoria + Custo
        col_img, col_info = st.columns([1, 3])
        with col_img:
            if pd.notna(item_row["imagem"]) and item_row["imagem"]:
                st.image(item_row["imagem"], width=46)
        with col_info:
            st.markdown(f"**{item_row['item']}**")
            st.caption(f"{item_row['categoria']} • <span class='soul-chip'>💰 {item_row['custo']:,}</span>", unsafe_allow_html=True)

        st.markdown("<div style='margin-top: 4px;'></div>", unsafe_allow_html=True)

        # 2. Métricas de Desempenho (Linha com alinhamento fixo)
        c_wr, c_pick = st.columns(2)
        with c_wr:
            wr_val = item_row["winrate_pct"]
            wr_icon = "🔥" if wr_val >= 53.0 else ("🟢" if wr_val >= 50.0 else "⚪")
            st.markdown(f"**{wr_icon} {wr_val:.1f}%** WR")
        with c_pick:
            st.markdown(f"📊 **{item_row['pick_pct']:.1f}%** Pick")

        # 3. Popover Flutuante (NÃO quebra a altura do card como o expander fazia!)
        desc_text = item_row.get("descricao")
        if desc_text:
            with st.popover("ℹ️ Ver efeito do item", use_container_width=True):
                st.markdown(f"#### {item_row['item']}")
                st.caption(f"{item_row['categoria']} • Tier {item_row.get('tier', 1)} • Custo: {item_row['custo']:,} Almas")
                st.markdown("---")
                st.markdown(desc_text)
        else:
            safe_id = item_row.get("item_id", item_row.get("item", "id"))
            safe_stage = item_row.get("game_stage", "stage")
            st.button("Sem efeitos adicionais", disabled=True, use_container_width=True, key=f"btn_disabled_{safe_id}_{safe_stage}")


def main():
    st.title("⚡ Deadlock Analytics")
    st.caption("Estatísticas oficiais, Guias de Builds e Meta competitivo.")

    try:
        df_heroes = load_heroes_data()
        df_items = load_items_catalog()
        df_builds = load_hero_builds()
    except Exception as e:
        st.error(f"❌ Erro ao conectar ao banco de dados: {e}")
        st.info("Execute `python src/main.py` para carregar as tabelas no PostgreSQL.")
        return

    # --- Navegação Integrada estilo Mobalytics / OP.GG ---
    tab_tierlist, tab_guide, tab_catalog, tab_matrix = st.tabs([
        "🏆 Tier List do Meta",
        "⚡ Guia de Build & Raio-X",
        "📦 Catálogo de Itens",
        "📊 Matriz do Meta",
    ])

    # =========================================================================
    # ABA 1: TIER LIST DO META (Ranking Geral - Abre como tela inicial)
    # =========================================================================
    with tab_tierlist:
        roles = ["Todos", "🎯 Atirador / DPS", "🔮 Místico / Habilidades", "⚔️ Lutador / Frontline"]
        selected_role = st.segmented_control("Filtrar por Estilo de Jogo:", options=roles, default="Todos")

        filtered_df = df_heroes if selected_role == "Todos" else df_heroes[df_heroes["tipo"] == selected_role]

        if len(filtered_df) >= 3:
            st.markdown("#### 🌟 Top 3 do Meta")
            podium_cols = st.columns(3)
            medals = ["🥇 1º Lugar", "🥈 2º Lugar", "🥉 3º Lugar"]
            for i in range(3):
                h = filtered_df.iloc[i]
                with podium_cols[i]:
                    with st.container(border=True):
                        c_img, c_info = st.columns([1, 2])
                        with c_img:
                            if pd.notna(h["avatar"]):
                                st.image(h["avatar"], width=65)
                        with c_info:
                            st.markdown(f"**{medals[i]}**")
                            st.markdown(f"### {h['heroi']}")
                            st.caption(f"{h['tipo']} • Tier **{h['tier']}**")
                        st.metric("Win Rate", f"{h['win_rate']:.2f}%", f"Pick: {h['pick_rate']:.1f}%")

            st.markdown("---")

        st.markdown("#### 📋 Classificação Completa")
        table_view = filtered_df[["tier", "avatar", "heroi", "tipo", "win_rate", "pick_rate", "kda", "partidas"]].copy()
        st.dataframe(
            table_view,
            column_config={
                "tier": st.column_config.TextColumn("Tier", width="small"),
                "avatar": st.column_config.ImageColumn("Herói", width="small"),
                "heroi": st.column_config.TextColumn("Nome"),
                "tipo": st.column_config.TextColumn("Função"),
                "win_rate": st.column_config.ProgressColumn("Taxa de Vitória", format="%.2f%%", min_value=40.0, max_value=60.0),
                "pick_rate": st.column_config.NumberColumn("Popularidade", format="%.2f%%"),
                "kda": st.column_config.TextColumn("KDA Médio"),
                "partidas": st.column_config.NumberColumn("Partidas", format="%d"),
            },
            hide_index=True,
            use_container_width=True,
            height=450,
        )

    # =========================================================================
    # ABA 2: GUIA E BUILD DO HERÓI (ESTILO MOBALYTICS COM RAIO-X INTEGRADO)
    # =========================================================================
    with tab_guide:
        # Seletor com heróis ordenados
        hero_names = sorted(df_heroes["heroi"].unique())
        selected_hero = st.selectbox(
            "Selecione um Herói para ver a Build completa e o Raio-X:",
            options=hero_names,
            index=hero_names.index("Infernus") if "Infernus" in hero_names else 0,
        )

        hero = df_heroes[df_heroes["heroi"] == selected_hero].iloc[0]
        hero_build = df_builds[df_builds["heroi"] == selected_hero]

        # --- 1. BANNER DO HERÓI (RAIO-X ESTILO MOBALYTICS) ---
        with st.container(border=True):
            b_avatar, b_info, b_wr, b_pick, b_kda = st.columns([1, 2.5, 1.2, 1.2, 1.2])
            with b_avatar:
                if pd.notna(hero["avatar"]):
                    st.image(hero["avatar"], width=105)
            with b_info:
                badge_class = f"badge-tier-{hero['tier'].lower()}"
                st.markdown(f"## {hero['heroi']} <span class='{badge_class}'>TIER {hero['tier']}</span>", unsafe_allow_html=True)
                st.caption(f"{hero['tipo']} • Analisado em {hero['partidas']:,} partidas")
                
                if hero["win_rate"] >= 52.0:
                    st.success("🔥 **Meta Pick:** Desempenho excelente no patch atual!")
                elif hero["win_rate"] >= 49.5:
                    st.info("⚖️ **Balanceado:** Herói consistente e estável.")
                else:
                    st.warning("⚠️ **Desafiador:** Abaixo da média no patch atual.")

            with b_wr:
                st.metric("Taxa de Vitória", f"{hero['win_rate']:.2f}%", f"{hero['win_rate'] - 50.0:+.2f}%")
            with b_pick:
                st.metric("Taxa de Escolha", f"{hero['pick_rate']:.2f}%")
            with b_kda:
                st.metric("KDA Médio", hero["kda"])

        # --- 2. DISTRIBUIÇÃO DA BUILD (FOCO DO HERÓI) ---
        if not hero_build.empty:
            st.markdown("##### 🎯 Foco de Compra da Build:")
            slot_counts = hero_build["slot_type"].value_counts(normalize=True) * 100
            w_pct = slot_counts.get("weapon", 0.0)
            v_pct = slot_counts.get("vitality", 0.0)
            s_pct = slot_counts.get("spirit", 0.0)

            c_w, c_v, c_s = st.columns(3)
            with c_w:
                st.markdown(f"🟠 **Dano de Arma:** {w_pct:.1f}% dos itens")
            with c_v:
                st.markdown(f"🟢 **Vitalidade / Escudo:** {v_pct:.1f}% dos itens")
            with c_s:
                st.markdown(f"🟣 **Poder Místico:** {s_pct:.1f}% dos itens")

        st.markdown("---")

        # --- 3. TIMELINE DA BUILD (EARLY, MID, LATE GAME) ---
        st.subheader("🛠️ Ordem de Compra Recomendada (Build Path)")
        st.caption("Itens essenciais e mais eficientes ordenados pela taxa de vitória e popularidade dos melhores jogadores.")

        phases = [
            ("early_game", "🌅 1. Início de Jogo (Early Game • 0 a 10 min)", "Itens de rota para garantir sobrevivência e acelerar o farm de Almas:"),
            ("mid_game", "⚡ 2. Meio de Jogo (Mid Game • 10 a 20 min)", "Itens centrais de pico de poder (Power Spike) para vencer confrontos de equipe:"),
            ("late_game", "👑 3. Fim de Jogo (Late Game • 20+ min)", "Upgrades lendários de Tier 3 e 4 para garantir a vitória:"),
        ]

        for stage_key, stage_title, stage_desc in phases:
            st.markdown(f"#### {stage_title}")
            st.caption(stage_desc)

            stage_data = hero_build[hero_build["game_stage"] == stage_key]
            if stage_data.empty:
                st.info("Nenhum dado registrado para esta fase.")
            else:
                items_list = [row for _, row in stage_data.head(6).iterrows()]
                # Divide em linhas de 3 colunas independentes para alinhamento horizontal perfeito
                for r_idx in range(0, len(items_list), 3):
                    row_items = items_list[r_idx:r_idx + 3]
                    row_cols = st.columns(3)
                    for c_idx, item_row in enumerate(row_items):
                        with row_cols[c_idx]:
                            render_mobalytics_card(item_row)

            st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

    # =========================================================================
    # ABA 3: CATÁLOGO DE ITENS (LOJA DO JOGO)
    # =========================================================================
    with tab_catalog:
        st.markdown("#### 📦 Catálogo de Itens da Loja")
        col_cat, col_tier, col_search = st.columns([1, 1, 2])
        with col_cat:
            cat_filter = st.selectbox("Categoria:", ["Todas", "🟠 Arma", "🟢 Vitalidade", "🟣 Espírito"])
        with col_tier:
            tier_filter = st.selectbox("Tier / Custo:", ["Todos", "Tier 1 (500)", "Tier 2 (1.250)", "Tier 3 (3.000)", "Tier 4 (6.200)"])
        with col_search:
            search_term = st.text_input("🔍 Pesquisar por nome ou efeito:", placeholder="ex: lifesteal, cooldown, magazine...")

        filtered_items = df_items.copy()
        if cat_filter != "Todas":
            filtered_items = filtered_items[filtered_items["categoria"] == cat_filter]
        if tier_filter != "Todos":
            tier_num = int(tier_filter.split()[1])
            filtered_items = filtered_items[filtered_items["tier"] == tier_num]
        if search_term:
            filtered_items = filtered_items[
                filtered_items["item"].str.contains(search_term, case=False, na=False) |
                filtered_items["descricao"].str.contains(search_term, case=False, na=False)
            ]

        st.dataframe(
            filtered_items[["imagem", "item", "categoria", "tier", "custo", "tipo_habilidade", "descricao"]],
            column_config={
                "imagem": st.column_config.ImageColumn("Ícone", width="small"),
                "item": st.column_config.TextColumn("Item", width="medium"),
                "categoria": st.column_config.TextColumn("Categoria"),
                "tier": st.column_config.NumberColumn("Tier"),
                "custo": st.column_config.NumberColumn("Almas (Souls)", format="%d"),
                "tipo_habilidade": st.column_config.TextColumn("Tipo"),
                "descricao": st.column_config.TextColumn("Efeito / Descrição", width="large"),
            },
            hide_index=True,
            use_container_width=True,
            height=500,
        )

    # =========================================================================
    # ABA 4: GRÁFICO DO META
    # =========================================================================
    with tab_matrix:
        st.markdown("#### 📊 Mapa do Meta: Win Rate (%) vs. Popularidade (%)")
        fig = px.scatter(
            df_heroes,
            x="pick_rate",
            y="win_rate",
            color="tipo",
            hover_name="heroi",
            size="partidas",
            hover_data={"tipo": True, "win_rate": ":.2f", "pick_rate": ":.2f", "kda": True, "partidas": ":,", "avatar": False},
            labels={"pick_rate": "Popularidade (%)", "win_rate": "Taxa de Vitória (%)", "tipo": "Função", "partidas": "Total de Partidas"},
            height=500,
        )
        fig.add_hline(y=50.0, line_dash="dot", line_color="rgba(255, 255, 255, 0.4)", annotation_text="50% Win Rate")
        fig.update_layout(margin=dict(l=20, r=20, t=30, b=20), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        st.plotly_chart(fig, use_container_width=True)


if __name__ == "__main__":
    main()

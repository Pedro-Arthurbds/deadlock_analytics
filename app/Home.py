import json
import sys
from pathlib import Path

# Adiciona a pasta 'src' ao sys.path para importar o módulo database
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR / "src"))

import streamlit as st
import pandas as pd
import plotly.express as px
from database import engine

# --- Configuração da Página ---
st.set_page_config(
    page_title="Deadlock Meta & Analytics",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",  # Colapsado por padrão para tela limpa
)

# --- CSS Personalizado para Visual Moderno e Limpo ---
st.markdown("""
<style>
    /* Estilização suave para cards e métricas */
    .hero-card {
        background-color: #1a1c23;
        border-radius: 12px;
        padding: 20px;
        border: 1px solid #2d3139;
        margin-bottom: 20px;
    }
    .metric-value {
        font-size: 28px;
        font-weight: bold;
        color: #f0f2f6;
    }
    .metric-label {
        font-size: 14px;
        color: #8b949e;
        margin-bottom: 4px;
    }
    .badge-s { background-color: #ffb703; color: #000; font-weight: bold; padding: 3px 8px; border-radius: 6px; }
    .badge-a { background-color: #8ecae6; color: #000; font-weight: bold; padding: 3px 8px; border-radius: 6px; }
    .badge-b { background-color: #219ebc; color: #fff; font-weight: bold; padding: 3px 8px; border-radius: 6px; }
    .badge-c { background-color: #6c757d; color: #fff; font-weight: bold; padding: 3px 8px; border-radius: 6px; }
</style>
""", unsafe_allow_html=True)


def calculate_tier(win_rate: float) -> str:
    """Calcula o Tier do herói com base no Win Rate."""
    if win_rate >= 51.5:
        return "S"
    elif win_rate >= 50.0:
        return "A"
    elif win_rate >= 48.0:
        return "B"
    else:
        return "C"


def translate_type(hero_type: str) -> str:
    """Traduz o arquétipo técnico para nomes amigáveis em português."""
    translations = {
        "marksman": "🎯 Atirador",
        "mystic": "🔮 Místico",
        "brawler": "⚔️ Lutador",
        "Indefinido": "Outro",
    }
    return translations.get(str(hero_type).lower(), "Outro")


@st.cache_data(ttl=600)
def load_data() -> pd.DataFrame:
    """Carrega dados consolidados do PostgreSQL e enriquece com avatares."""
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
        df = pd.read_sql(query, con=conn)

    # Mapeia avatares dos heróis a partir do JSON bruto de heróis
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


def main():
    # --- Cabeçalho Limpo e Moderno ---
    st.title("⚡ Deadlock Analytics")
    st.caption("Guia rápido de heróis, estatísticas e meta atual para jogadores.")

    try:
        df = load_data()
    except Exception as e:
        st.error(f"❌ Não foi possível carregar os dados: {e}")
        st.info("Execute `src/main.py` e `src/hero_stats.py` para popular o banco de dados.")
        return

    # --- Navegação por Abas (Evita tela poluída!) ---
    tab_tierlist, tab_hero, tab_matrix = st.tabs([
        "🏆 Tier List do Meta",
        "🔍 Raio-X do Herói",
        "📊 Gráficos do Meta",
    ])

    # =========================================================================
    # ABA 1: TIER LIST (Visão Rápida para o Jogador)
    # =========================================================================
    with tab_tierlist:
        # Filtro horizontal simplificado
        roles = ["Todos", "🎯 Atirador", "🔮 Místico", "⚔️ Lutador"]
        selected_role = st.segmented_control(
            "Filtrar por Estilo de Jogo:",
            options=roles,
            default="Todos",
        )

        filtered_df = df if selected_role == "Todos" else df[df["tipo"] == selected_role]

        # Top 3 em destaque visual (Pódio)
        if len(filtered_df) >= 3:
            st.markdown("#### 🌟 Top 3 Melhores do Meta")
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

        # Tabela Limpa Estilo "Scoreboard" com Avatares e Barras de Progresso
        st.markdown("#### 📋 Classificação Completa")
        table_view = filtered_df[[
            "tier", "avatar", "heroi", "tipo", "win_rate", "pick_rate", "kda", "partidas"
        ]].copy()

        st.dataframe(
            table_view,
            column_config={
                "tier": st.column_config.TextColumn("Tier", width="small"),
                "avatar": st.column_config.ImageColumn("Herói", width="small"),
                "heroi": st.column_config.TextColumn("Nome"),
                "tipo": st.column_config.TextColumn("Função"),
                "win_rate": st.column_config.ProgressColumn(
                    "Taxa de Vitória",
                    help="Percentual de vitórias",
                    format="%.2f%%",
                    min_value=40.0,
                    max_value=60.0,
                ),
                "pick_rate": st.column_config.NumberColumn(
                    "Popularidade",
                    help="Frequência de escolha nas partidas",
                    format="%.2f%%",
                ),
                "kda": st.column_config.TextColumn("KDA Médio"),
                "partidas": st.column_config.NumberColumn("Partidas", format="%d"),
            },
            hide_index=True,
            use_container_width=True,
            height=450,
        )

    # =========================================================================
    # ABA 2: RAIO-X DO HERÓI (Consulta Individual Direta)
    # =========================================================================
    with tab_hero:
        st.markdown("#### 🔍 Escolha um Herói para ver o perfil completo:")
        hero_names = sorted(df["heroi"].unique())
        selected_hero_name = st.selectbox(
            "Selecione um herói:",
            options=hero_names,
            label_visibility="collapsed",
        )

        hero = df[df["heroi"] == selected_hero_name].iloc[0]

        # Card de Perfil do Herói
        with st.container(border=True):
            head_col1, head_col2 = st.columns([1, 4])
            with head_col1:
                if pd.notna(hero["avatar"]):
                    st.image(hero["avatar"], width=120)
            with head_col2:
                st.title(hero["heroi"])
                st.markdown(f"**Função:** {hero['tipo']} | **Classificação:** Tier **{hero['tier']}**")
                
                # Mensagem interpretativa para o jogador
                if hero["win_rate"] >= 51.5:
                    st.success("🔥 **Herói em Alta:** Desempenho excelente no meta atual! Excelente escolha para subir de rank.")
                elif hero["win_rate"] >= 49.5:
                    st.info("⚖️ **Equilibrado:** Herói balanceado e estável. Depende da habilidade mecânica do jogador.")
                else:
                    st.warning("⚠️ **Abaixo da Média:** Taxa de vitória menor no patch atual. Exige boa composição de equipe.")

            st.markdown("---")

            # 4 Métricas Chave em Caixas Limpas
            m1, m2, m3, m4 = st.columns(4)
            with m1:
                wr_delta = f"{hero['win_rate'] - 50.0:+.2f}% vs média"
                st.metric("Taxa de Vitória", f"{hero['win_rate']:.2f}%", wr_delta)
            with m2:
                st.metric("Popularidade (Pick Rate)", f"{hero['pick_rate']:.2f}%")
            with m3:
                st.metric("KDA Médio", hero["kda"])
            with m4:
                st.metric("Farm Médio (Souls)", f"{hero['avg_net_worth']:,.0f}")

    # =========================================================================
    # ABA 3: GRÁFICO DO META (Visão Analítica Sem Poluição)
    # =========================================================================
    with tab_matrix:
        st.markdown("#### 📊 Mapa do Meta: Win Rate (%) vs. Popularidade (%)")
        st.caption(
            "Passe o mouse por cima de cada ponto para ver os detalhes do herói sem poluir a tela."
        )

        fig = px.scatter(
            df,
            x="pick_rate",
            y="win_rate",
            color="tipo",
            hover_name="heroi",
            size="partidas",
            hover_data={
                "tipo": True,
                "win_rate": ":.2f",
                "pick_rate": ":.2f",
                "kda": True,
                "partidas": ":,",
                "avatar": False,
            },
            labels={
                "pick_rate": "Popularidade / Pick Rate (%)",
                "win_rate": "Taxa de Vitória / Win Rate (%)",
                "tipo": "Função",
                "partidas": "Total de Partidas",
            },
            height=500,
        )

        # Linha de 50% de Win Rate
        fig.add_hline(
            y=50.0,
            line_dash="dot",
            line_color="rgba(255, 255, 255, 0.4)",
            annotation_text="50% Win Rate",
            annotation_position="bottom left",
        )

        fig.update_layout(
            margin=dict(l=20, r=20, t=30, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )

        st.plotly_chart(fig, use_container_width=True)


if __name__ == "__main__":
    main()

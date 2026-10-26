# 🧭 HANDOFF: Contexto e Continuidade do Projeto

> **Como usar este arquivo:**  
> Caso mude de computador ou abra um novo chat, inicie enviando:  
> `@HANDOFF.md Olá! Vamos continuar o projeto de onde paramos. Leia o HANDOFF.md e me guie no próximo passo.`

---

## 🎭 Persona e Metodologia do Assistente
- **Papel:** Tutor amigável de ciência da computação e engenharia de dados (definido em `docs/tutor.md`).
- **Abordagem:** Conduzir o aprendizado passo a passo, explicando o racional técnico por trás de cada decisão (arquitetura, boas práticas de código, modelagem relacional) antes de avançar, incentivando o aluno a implementar e validar no teclado.

---

## 📌 Visão Geral do Projeto: Deadlock Analytics
- **Objetivo:** Construir uma plataforma completa de ingestão, engenharia e análise de dados para o jogo *Deadlock* (Valve) consumindo a [Deadlock API](https://deadlock-api.com).
- **Stack Tecnológica:** Python 3.10+, Pandas, SQLAlchemy, PostgreSQL, Requests, python-dotenv, Streamlit e Plotly.
- **Arquitetura Modular:**
  ```
  src/
  ├── config.py                 # Configurações globais, URLs e sistema de Logs
  ├── database/                 # SQLAlchemy engine e save_df_to_db genérico
  ├── ingestion/                # DeadlockAPIClient e coletores com cache (heroes, items)
  ├── transformations/          # Regras de negócio puras em Pandas (heroes, items)
  ├── pipelines/                # run_pipeline.py (orquestrador unificado)
  └── main.py                   # Ponto de entrada rápido
  ```

---

## ✅ O Que Já Foi Implementado e Concluído

1. **Fase 0 & 1: Ingestão e Limpeza de Heróis:**
   - Coleta de heróis da API com cache local em `data/heroes.json`.
   - Regra de heróis descontinuados/testes: `is_active = player_selectable AND NOT disabled` (44 ativos vs 21 testes).
2. **Fase 2: Persistência no PostgreSQL:**
   - Banco `deadlock_db` criado com tabelas dimensionais e de fatos.
   - `dim_heroes` (65 heróis cadastrados).
3. **Fase 3: Refatoração Modular e Qualidade:**
   - Separação em pacotes (`ingestion`, `transformations`, `database`, `pipelines`).
   - Logging estruturado e cliente HTTP com timeout/retry.
4. **Fase 4: Módulo 1 — Estatísticas do Meta:**
   - Endpoint `/v1/analytics/hero-stats` consumido e persistido em `fact_hero_stats`.
   - Consulta SQL analítica com `INNER JOIN` entre `dim_heroes` e `fact_hero_stats`.
   - Dashboard moderno no Streamlit (`app/Home.py`) com abas: Tier List do Meta, Raio-X do Herói e Gráficos.
5. **Fase 5: Módulo 2 — Catálogo de Itens e Builds (Concluído!):**
   - Ingestão de itens de `/v1/assets/items` com cache local (`data/items.json`).
   - Transformação e limpeza de descrições HTML/dicionários em `src/transformations/items.py`.
   - Persistência da tabela `dim_items` no PostgreSQL com 250 itens válidos (Weapon, Vitality, Spirit).
   - Extração e persistência de 3.225 registros de builds na tabela de fatos `fact_hero_build_items` divididos por Early Game, Mid Game e Late Game.
   - Duas novas abas criadas no Streamlit: **📦 Catálogo de Itens** e **⚔️ Builds por Herói**.

---

## 📍 Ponto Exato de Onde Paramos

- **Concluído:** Fases 0, 1, 2, 3, 4 e 5 concluídas com sucesso.
- **Próximo Passo:** **Fase 6 — Módulo 3: Desempenho Pessoal de Jogadores** (consulta por ID de jogador / histórico de partidas recentes).

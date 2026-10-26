# 🧭 HANDOFF: Contexto e Continuidade do Projeto

> **Como usar este arquivo:**  
> No outro computador, abra o projeto no Antigravity e inicie um novo chat enviando:  
> `@HANDOFF.md Olá! Vamos continuar o projeto de onde paramos. Leia o HANDOFF.md e me guie no próximo passo do arquivo src/hero_stats.py.`

---

## 🎭 Persona e Metodologia do Assistente
- **Papel:** Tutor amigável de ciência da computação e engenharia de dados (definido em `docs/tutor.md`).
- **Abordagem:** Conduzir o aprendizado passo a passo, explicando o racional técnico por trás de cada decisão (arquitetura, boas práticas de código, modelagem relacional) antes de avançar, incentivando o aluno a implementar e validar.

---

## 📌 Visão Geral do Projeto: Deadlock Analytics
- **Objetivo:** Construir uma plataforma completa de ingestão, engenharia e análise de dados para o jogo *Deadlock* (Valve) consumindo a [Deadlock API](https://deadlock-api.com).
- **Stack Tecnológica:** Python 3.10+, Pandas, SQLAlchemy, PostgreSQL, Requests, python-dotenv (futuramente Streamlit e Plotly para dashboards).
- **Arquitetura:** Pipeline clássico em camadas:
  1. *Raw/Cache:* Dados brutos em JSON (`data/heroes.json`).
  2. *Transform:* Limpeza, modelagem dimensional e regras de negócio com Pandas.
  3. *Load/Storage:* Banco relacional PostgreSQL (`deadlock_db`).
  4. *Serving/Analytics:* Consultas SQL analíticas e visualizações.

---

## ✅ O Que Já Foi Implementado e Concluído

1. **Estrutura Base e Dependências:**
   - Ambiente virtual `.venv` configurado.
   - Dependências em `requirements.txt`: `requests`, `pandas`, `SQLAlchemy`, `psycopg2-binary`, `python-dotenv`.
   - `.gitignore` protegendo `.env` e `.venv/`.

2. **Ingestão & Cache de Heróis (`src/main.py`):**
   - Consumo do endpoint `/v1/assets/heroes` da Deadlock API.
   - Salvamento de cache local em `data/heroes.json` para economizar requisições e permitir testes offline.
   - Função de transformação `transform_heroes` para filtrar colunas essenciais e aplicar regra de negócio:
     `is_active = player_selectable AND NOT disabled` (diferencia heróis oficiais de heróis protótipo/descontinuados da Valve).

3. **Banco de Dados Relacional (`src/database.py`):**
   - Configuração de conexão com PostgreSQL via SQLAlchemy e psycopg2 com credenciais no `.env`.
   - Função `test_connection()` com verificação de status.
   - Função `save_heroes_to_db()` que persiste o DataFrame na tabela dimensional `dim_heroes`.
   - Validada a persistência de 65 heróis (44 ativos e 21 inativos/desenvolvimento).

---

## 📍 Ponto Exato de Onde Paramos

- **Arquivo atual:** `src/hero_stats.py`
- **Estado do arquivo:** O arquivo foi recém-criado e possui apenas a estrutura inicial de imports:
  ```python
  import json
  from pathlib import Path
  import pandas
  ```
- **Fase atual no Roadmap:** **Fase 4 (Módulo 1 — Estatísticas e Análise dos Heróis)**.
  - Precisamos explorar e consumir o endpoint de estatísticas de heróis da Deadlock API (`/v1/analytics/hero-stats` ou equivalente documentado em `docs/api.md`).
  - Estruturar a camada de ingestão e transformação das métricas (Win Rate, Pick Rate, partidas jogadas).
  - Modelar e persistir esses dados na tabela de fatos `fact_hero_stats` no PostgreSQL para posterior relacionamento com `dim_heroes`.

---

## 🚀 Próximos Passos Imediatos para o Novo Computador

1. **Configurar o Ambiente na nova máquina:**
   ```bash
   # Clonar/abrir a pasta do projeto
   cd deadlock_api
   
   # Criar e ativar o ambiente virtual
   python3 -m venv .venv
   source .venv/bin/activate  # ou .venv\Scripts\activate no Windows
   pip install -r requirements.txt
   ```
2. **Configurar o PostgreSQL na nova máquina:**
   - Criar o banco de dados `deadlock_db`:
     ```sql
     CREATE DATABASE deadlock_db;
     ```
   - Criar o arquivo `.env` na raiz do projeto:
     ```env
     DB_HOST=localhost
     DB_PORT=5432
     DB_NAME=deadlock_db
     DB_USER=seu_usuario
     DB_PASSWORD=sua_senha
     ```
   - Testar a conexão rodando:
     ```bash
     python src/database.py
     ```
3. **Continuar o Desenvolvimento:**
   - Abrir o chat do Antigravity e pedir para implementar o pipeline em `src/hero_stats.py`.


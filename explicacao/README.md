# 🎓 Aula Prática: Da Máquina Local à Nuvem com PostgreSQL (Neon) & Streamlit Cloud

> **Professor:** Seu Assistente de Engenharia de Dados & Arquitetura  
> **Projeto:** *Deadlock Analytics*  
> **Objetivo:** Compreender a transição de uma aplicação local (onde tudo roda no seu computador) para uma arquitetura profissional e distribuída na nuvem (banco de dados no Neon e dashboard no Streamlit Cloud).

---

## 🧭 Sumário da Aula

1. [A Grande Virada: O que tínhamos vs. O que temos agora](#1-a-grande-virada-o-que-tínhamos-vs-o-que-temos-agora)
2. [Conceito 1: Por que o `localhost` não funciona na nuvem?](#2-conceito-1-por-que-o-localhost-não-funciona-na-nuvem)
3. [Conceito 2: O que é o Neon e o PostgreSQL Serverless?](#3-conceito-2-o-que-é-o-neon-e-o-postgresql-serverless)
4. [Conceito 3: A Anatomia de uma Connection String](#4-conceito-3-a-anatomia-de-uma-connection-string)
5. [Conceito 4: SQLAlchemy, Drivers e o `psycopg2`](#5-conceito-4-sqlalchemy-drivers-e-o-psycopg2)
6. [O Código em Detalhes: Entendendo o `src/config.py`](#6-o-código-em-detalhes-entendendo-o-srcconfigpy)
7. [Segurança & Deploy: `.env`, `.gitignore` e `Streamlit Secrets`](#7-segurança--deploy-env-gitignore-e-streamlit-secrets)
8. [A Sala de Autópsia: Entendendo os Erros que Aconteceram](#8-a-sala-de-autópsia-entendendo-os-erros-que-aconteceram)
9. [Checklist de Bolso para Seus Futuros Projetos](#9-checklist-de-bolso-para-seus-futuros-projetos)

---

## 1. A Grande Virada: O que tínhamos vs. O que temos agora

Antes desta aula, o seu projeto funcionava em uma arquitetura puramente **monolítica local**:

```mermaid
flowchart LR
    subgraph Seu Computador
        A[Terminal / Python] -->|Grava dados| B[(PostgreSQL Local\nlocalhost:5432)]
        C[Streamlit Local\nlocalhost:8501] -->|Lê dados| B
    end
```

**O problema desse modelo:**
- Se o seu computador for desligado, ninguém mais acessa o banco nem o dashboard.
- Se você enviar o link do Streamlit para um amigo ou recrutador, a aplicação na nuvem não conseguirá "enxergar" o banco que está dentro do seu disco rígido.

Agora, migramos para uma **arquitetura moderna em nuvem distribuída**:

```mermaid
flowchart TD
    subgraph Máquina Local
        DEV[Seu Computador / Terminal]
        ETL[Script ETL: python src/main.py]
    end

    subgraph Nuvem AWS / Neon
        NEON[(Neon Serverless Postgres\nep-orange-dawn...neon.tech)]
    end

    subgraph Nuvem Streamlit
        CLOUD[Streamlit Community Cloud\nshare.streamlit.io]
    end

    DEV -->|1. git push com código| GITHUB[Repositório GitHub]
    GITHUB -->|2. Atualização automática| CLOUD
    ETL -->|3. Extrai da API Deadlock e envia via SSL| NEON
    CLOUD -->|4. Lê dados via SSL usando Secrets| NEON
    USER[Qualquer Usuário na Web] -->|5. Acessa pelo navegador| CLOUD
```

Ambos os serviços (Streamlit Cloud e o seu script local) agora conversam com a mesma fonte da verdade: **o banco remoto no Neon**.

---

## 2. Conceito 1: Por que o `localhost` não funciona na nuvem?

Quando você está aprendendo, é comum usar `localhost` ou `127.0.0.1`. Mas o que isso significa literalmente?

> [!NOTE]
> `localhost` é o apelido de rede para **"eu mesmo"** (esta própria máquina em que o código está rodando).

Pense na seguinte analogia do dia a dia:
- Se você está dentro do seu quarto e fala *"vou abrir a geladeira"*, você se refere à geladeira da **sua** casa.
- Se você liga para um amigo que está em outra cidade e diz *"abra a geladeira"*, ele vai abrir a geladeira da casa dele, não a sua!

Quando você colocou o Streamlit para rodar no **Streamlit Cloud**:
1. O Streamlit criou uma máquina virtual isolada em servidores nos EUA.
2. Seu código disse: *"Conecte no banco em `localhost:5432`"*.
3. O servidor do Streamlit procurou um PostgreSQL dentro **dele mesmo**.
4. Como não havia nenhum banco instalado naquela máquina virtual, ele respondeu:
   ```text
   Connection refused: Is the server running on that host and accepting TCP/IP connections?
   ```

**A lição:** Na nuvem, nenhuma aplicação pode apontar para `localhost`, a menos que o banco esteja instalado dentro do mesmo container. Se o banco está em outro lugar, precisamos de um endereço público acessível via internet (uma URL pública).

---

## 3. Conceito 2: O que é o Neon e o PostgreSQL Serverless?

Você já deve ter ouvido falar que para ter um banco na nuvem antigamente precisávamos:
1. Alugar uma máquina virtual (VPS) na AWS (EC2) ou DigitalOcean.
2. Instalar o Linux, configurar portas, instalar o PostgreSQL na mão.
3. Deixar a máquina ligada 24 horas por dia pagando em dólares por hora.

### O que torna o Neon especial?
O **Neon** é um banco de dados PostgreSQL **Serverless**:
- **Desacoplamento de Computação e Armazenamento:** Se ninguém estiver usando o banco, o processador entra em modo "hibernação" (Scale to Zero), custando **zero**.
- **Ativação Instantânea:** No momento em que uma consulta SQL chega, ele "acorda" em milissegundos.
- **Gratuito para Projetos e Portfólios:** Não exige cartão de crédito no plano inicial e oferece recursos suficientes para projetos profissionais.

---

## 4. Conceito 3: A Anatomia de uma Connection String

O Neon fornece para você uma **Connection String** (URL de conexão). Ela parece uma sopa de letrinhas à primeira vista, mas veja como ela é perfeitamente organizada:

```text
postgresql://neondb_owner:npg_1yLVPkqZur9t@ep-orange-dawn-b4mtehfz-pooler.c-6.us-east-2.aws.neon.tech/neondb?sslmode=require
│          │            │                │                                                           │       │
│          │            │                │                                                           │       └─ 6. Parâmetros (SSL Obrigatório)
│          │            │                │                                                           └───────── 5. Nome do Banco de Dados
│          │            │                └───────────────────────────────────────────────────────────────────── 4. Host (Endereço do Servidor)
│          │            └────────────────────────────────────────────────────────────────────────────────────── 3. Senha Secreta
│          └─────────────────────────────────────────────────────────────────────────────────────────────────── 2. Usuário
└────────────────────────────────────────────────────────────────────────────────────────────────────────────── 1. Protocolo / SGDB
```

### Por que o `sslmode=require` é crucial?
No seu computador local (`localhost`), o tráfego de dados não sai da sua placa-mãe. Mas quando conectamos ao Neon, os dados trafegam pela internet pública mundial!
O `sslmode=require` força a conexão a ser **100% criptografada com TLS/SSL**. Se alguém interceptar os pacotes de rede entre sua casa e a AWS, só verá dados embaralhados e indecifráveis. O Neon **recusa** conexões que não utilizem SSL.

---

## 5. Conceito 4: SQLAlchemy, Drivers e o `psycopg2`

No ecossistema Python, conectar ao banco exige duas camadas trabalhando juntas:

```mermaid
flowchart LR
    A[Seu Código Python / Pandas] --> B[SQLAlchemy: Gerenciador de Alto Nível]
    B --> C[psycopg2: O Driver de Rede de Baixo Nível]
    C --> D[(PostgreSQL Neon)]
```

1. **SQLAlchemy:** É a biblioteca que traduz comandos Python em SQL, gerencia conexões, cria pools e converte DataFrames do Pandas em tabelas.
2. **psycopg2:** É o **driver** (escrito em C). É ele quem realmente sabe abrir um socket TCP de rede, falar o dialeto binário do PostgreSQL e enviar a senha com criptografia.

### A Pegadinha do Prefixo no SQLAlchemy
Se você entregar para o SQLAlchemy moderno uma URL que começa com:
`postgresql://...`
Ele tenta descobrir qual driver usar. Para evitar ambiguidades e garantir que o driver correto (`psycopg2`) seja acionado, a convenção padrão do SQLAlchemy é:
`postgresql+psycopg2://...`

Se você passar `postgres://` (um formato antigo muito usado no Heroku), versões recentes do SQLAlchemy quebram com o erro:
`NoSuchModuleError: Can't load plugin: sqlalchemy.dialects:postgres`

Por isso nós criamos uma regra inteligente no código para tratar essa URL!

---

## 6. O Código em Detalhes: Entendendo o `src/config.py`

Vamos dissecar o código que criamos em [`src/config.py`](file:///home/pedroarthur/Documents/Github/deadlock_analytics/src/config.py). Ele foi projetado usando o padrão de **Fallback em Cascata**:

```python
# --- Configurações do PostgreSQL ---

# 1. Primeiro: tenta ler a variável DATABASE_URL do arquivo .env local
DATABASE_URL = os.getenv("DATABASE_URL")

# 2. Segundo: se não achou no .env, verifica se estamos rodando dentro do Streamlit Cloud
if not DATABASE_URL:
    try:
        import streamlit as st
        if hasattr(st, "secrets") and "DATABASE_URL" in st.secrets:
            DATABASE_URL = st.secrets["DATABASE_URL"]
    except Exception:
        pass

# 3. Terceiro: se ainda assim não achou, monta a URL com os parâmetros locais padrão
if not DATABASE_URL:
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "deadlock_db")
    DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# 4. Quarto: higienização e compatibilidade de prefixos
elif DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg2://", 1)
elif DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1)
```

### Por que esse design é excelente?
- **Ambiente Híbrido:** O mesmo código funciona sem você mexer em nada na sua máquina local, no servidor de homologação ou na nuvem de produção.
- **Resiliente:** Se você esquecer um prefixo ou se o provedor mudar ligeiramente a string, o código corrige em tempo de execução.
- **Desacoplado:** O Streamlit não precisa saber que o Neon existe; ele só consome uma conexão padronizada.

---

## 7. Segurança & Deploy: `.env`, `.gitignore` e `Streamlit Secrets`

Uma das regras de ouro do desenvolvimento de software profissional:
> [!CAUTION]
> **NUNCA, JAMAIS suba senhas, chaves de API ou strings de conexão com credenciais para o Git ou GitHub!**

Existem milhares de bots automáticos na internet escaneando commits públicos no GitHub a cada segundo em busca de senhas de banco para roubar dados ou instalar mineradores de criptomoedas.

### Como funciona a barreira de segurança?

1. **O arquivo `.env`:** Fica apenas no seu computador. Ele guarda suas senhas locais.
2. **O arquivo `.gitignore`:** Contém a linha `.env`. Quando você executa `git add .` ou `git status`, o Git simplesmente finge que o arquivo `.env` não existe.
3. **Mas e a nuvem? Como o Streamlit Cloud sabe a senha se o `.env` não vai para o GitHub?**
   É aqui que entra o **Secrets Management** do Streamlit!

No painel do Streamlit Cloud (`Settings` > `Secrets`), você fornece as credenciais diretamente na interface da nuvem:

```toml
DATABASE_URL = "postgresql://neondb_owner:npg_1yLVPkqZur9t@.../neondb?sslmode=require"
```

O Streamlit Cloud injeta essa variável em memória de forma segura para o seu código, sem que nenhuma linha de senha fique visível no seu código-fonte do GitHub.

---

## 8. A Sala de Autópsia: Entendendo os Erros que Aconteceram

Erros em programação não são falhas pessoais; são diagnósticos precisos do sistema. Vamos analisar os dois erros encontrados e o que eles nos ensinaram:

---

### Caso 1: `ModuleNotFoundError: No module named 'sqlalchemy'`

#### Sintoma:
Você digitou `python src/main.py` e o terminal cuspiu o erro de módulo não encontrado.

#### A Causa Raiz:
No Linux/macOS/Windows, você pode ter vários "Pythons" instalados.
- Existe o **Python do Sistema** (global), que o seu sistema operacional usa para tarefas dele.
- Existe o **Ambiente Virtual (`.venv`)**, que é uma pasta isolada criada especificamente para o seu projeto `deadlock_analytics`.

Todas as bibliotecas (`SQLAlchemy`, `pandas`, `psycopg2`) foram instaladas dentro da pasta `.venv`. Quando você executou apenas `python`, o terminal chamou o Python do sistema (onde nada estava instalado).

#### Como diagnosticar:
Basta perguntar ao terminal qual Python ele está usando:
```bash
which python
```
- Se responder `/usr/bin/python`, você está fora da venv!
- Se responder `/.../deadlock_analytics/.venv/bin/python`, você está dentro da venv!

#### Soluções definitivas:
1. Ativar o ambiente virtual antes de trabalhar:
   ```bash
   source .venv/bin/activate
   ```
2. Ou apontar diretamente para o executável da pasta `.venv`:
   ```bash
   .venv/bin/python src/main.py
   ```

---

### Caso 2: `(psycopg2.OperationalError) connection to server at "localhost" failed: Connection refused`

#### Sintoma:
Ao abrir o app hospedado no Streamlit Cloud, apareceu uma tela vermelha dizendo que a conexão com `localhost:5432` foi recusada.

#### A Linha do Tempo da Falha:
1. O código foi publicado no GitHub sem as novas linhas do `config.py`.
2. O Streamlit Cloud iniciou o app.
3. Não havia `.env` no repositório (corretamente ignorado).
4. O código antigo caiu no fallback: `DB_HOST = "localhost"`.
5. O Streamlit Cloud tentou bater na porta 5432 do próprio servidor dele.
6. Não havia nenhum Postgres ouvindo naquela porta, gerando o clássico `Connection refused`.

#### A Correção em 2 Etapas:
1. **No código:** Atualizar `config.py` para consultar `st.secrets` e fazer o `git push`.
2. **Na plataforma:** Cadastrar a variável `DATABASE_URL` na aba **Secrets** do Streamlit Cloud.

---

### Caso 3: `Can't reconnect until invalid transaction is rolled back. Please rollback() fully before proceeding` (A Soneca do Neon)

#### Sintoma:
Você entra no link do Streamlit após algum tempo inativo e vê uma mensagem vermelha de erro de transação inválida. Porém, **ao dar F5 (recarregar a página), o erro some e os dados aparecem normalmente!**

#### A Causa Raiz:
1. **O Neon Hiberna (Scale-to-Zero):** Como o Neon é um banco serverless gratuito, quando ele passa cerca de 5 minutos sem receber consultas, ele desliga a máquina para economizar recursos.
2. **A Conexão Zumbi do SQLAlchemy:** O Streamlit Cloud continuou ligado e o SQLAlchemy guardou conexões antigas na memória (connection pool).
3. **O Conflito:** Quando você abriu o site, o SQLAlchemy tentou reutilizar aquela conexão antiga sem testá-la antes. Como o Neon já havia encerrado a conexão do lado dele enquanto dormia, a consulta do Streamlit falhou na hora. O SQLAlchemy marcou a transação como "inválida/abortada".
4. **Por que o F5 resolvia?**
   - O primeiro erro "acordou" o Neon.
   - O erro fez o pool descartar a conexão quebrada.
   - No F5, o Neon já estava 100% acordado e uma nova conexão limpa foi criada com sucesso!

#### A Solução Definitiva no Código:
Configurar o `create_engine` com `pool_pre_ping=True` e `pool_recycle=300`:

```python
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # "Pinga" o banco com SELECT 1 antes de usar. Se o Neon estava dormindo, descarta a conexão velha e reconecta silenciosamente!
    pool_recycle=300,    # Recicla conexões a cada 5 minutos para evitar conexões expiradas no pool.
)
```

Com esses dois parâmetros, o usuário comum **nunca mais** verá a tela de erro, pois o SQLAlchemy acorda o banco e se reconecta nos bastidores antes de renderizar os gráficos!

---

## 9. Checklist de Bolso para Seus Futuros Projetos

Guarde este passo a passo para qualquer aplicação futura com Python + Banco na Nuvem + Streamlit:

- [ ] **Passo 1 (Banco):** Crie o banco no Neon (ou Supabase/ElephantSQL) e guarde a Connection String com `sslmode=require`.
- [ ] **Passo 2 (Local):** Coloque a URL no seu arquivo `.env` local: `DATABASE_URL=postgresql://...`.
- [ ] **Passo 3 (Git):** Verifique se o `.gitignore` possui `.env` e `.venv/`.
- [ ] **Passo 4 (Código):** Garanta que seu arquivo de configuração trate `postgresql://` -> `postgresql+psycopg2://` e busque em `st.secrets`.
- [ ] **Passo 5 (Carga):** Rode o pipeline ou script ETL localmente uma vez (`python src/main.py`) para criar as tabelas e subir os dados para o banco na nuvem.
- [ ] **Passo 6 (Git Push):** Suba o código atualizado para o GitHub (`git add .`, `git commit`, `git push`).
- [ ] **Passo 7 (Nuvem):** No Streamlit Cloud, configure a `DATABASE_URL` na seção de **Secrets**.
- [ ] **Passo 8 (Sucesso):** Recarregue o dashboard e veja a aplicação rodando no ar 24/7 para qualquer pessoa do mundo!

---

> 💡 **Mensagem do Professor:** Parabéns por ter chegado até aqui! A passagem do ambiente local para o ambiente em nuvem é exatamente o degrau que separa projetos de teste de **projetos de nível profissional prontos para produção**. Guarde esta pasta como sua referência sempre que iniciar um novo projeto!


Deadlock Analytics — Roadmap do Projeto
Objetivo: desenvolver uma plataforma de análise de dados do jogo Deadlock, utilizando a Deadlock API para construir dashboards, análises estatísticas de heróis, eficiência de itens e builds, acompanhamento de jogadores e análise de partidas.

Perfil do desenvolvedor: conhecimentos de Python, Pandas, SQL e PostgreSQL, com foco em aprender a estruturar e desenvolver projetos de dados completos.

1. Visão geral

O Deadlock Analytics será uma aplicação de análise de dados que transforma dados públicos do jogo em informações úteis para jogadores e interessados em estatísticas competitivas.

O projeto será desenvolvido incrementalmente. Cada etapa deverá gerar um resultado funcional e servir de base para a próxima.

Objetivos principais
Consumir dados da Deadlock API.
Desenvolver um pipeline de ingestão, transformação e armazenamento.
Modelar os dados em um banco PostgreSQL.
Construir indicadores estatísticos utilizando SQL e Pandas.
Criar dashboards interativos.
Analisar heróis, itens, builds, jogadores e partidas.
Desenvolver boas práticas de organização, testes, documentação e versionamento.
Criar um projeto demonstrável para portfólio.
Princípios de desenvolvimento
Construir uma funcionalidade por vez.
Priorizar simplicidade antes de adicionar complexidade.
Validar os dados disponíveis antes de definir a modelagem final.
Separar coleta, transformação, persistência e apresentação.
Evitar duplicação de código e de registros.
Documentar as decisões técnicas relevantes.
Aprender os conceitos durante a implementação, sem tentar dominar todas as ferramentas antecipadamente. 2. Escopo funcional

A plataforma será dividida em quatro módulos analíticos.

Módulo 1 — Meta e estatísticas de heróis

Objetivo: entender o desempenho e a popularidade dos heróis em diferentes contextos.

Funcionalidades previstas:

Listagem e pesquisa de heróis.
Taxa de vitória (win rate).
Taxa de escolha (pick rate).
Quantidade de partidas analisadas.
Filtros por período, patch e rank, conforme os dados disponíveis.
Comparação entre heróis.
Evolução dos indicadores ao longo do tempo.
Identificação de variações de popularidade e desempenho.
Análise de sinergias e counters, em uma etapa posterior.

Visualizações previstas:

Ranking de heróis.
Gráfico de win rate versus pick rate.
Séries temporais.
Comparação entre heróis.
Tabelas com filtros.
Módulo 2 — Eficiência de itens e builds

Objetivo: investigar quais itens e combinações estão associados a melhores resultados.

Funcionalidades previstas:

Catálogo de itens.
Frequência de utilização ou compra.
Win rate associado aos itens.
Builds mais utilizadas por herói.
Comparação entre builds alternativas.
Ordem de compra dos itens.
Momento da compra, quando disponível.
Análise por rank e patch.
Evolução das builds ao longo do tempo.
Comparação entre partidas vencidas e perdidas.

Visualizações previstas:

Ranking de itens.
Comparação de builds.
Combinações de itens.
Linha do tempo das compras.
Tabelas de eficiência com quantidade de observações.

Cuidado analítico: o desempenho associado a um item não demonstra que o item causou a vitória. Contexto da partida, habilidade do jogador, composição da equipe e seleção de itens podem influenciar o resultado.

A definição de uma build deverá ser estabelecida antes dos cálculos. Ela pode representar um conjunto de itens, uma sequência de compras ou uma combinação de itens para um determinado herói.

Módulo 3 — Desempenho pessoal

Objetivo: permitir que um jogador acompanhe seus resultados e identifique padrões de desempenho.

Funcionalidades previstas:

Consulta de jogadores por identificador compatível com a API.
Histórico de partidas.
Vitórias e derrotas.
Desempenho por herói.
Evolução do rank, se houver dados históricos suficientes.
Comparação entre períodos.
Análise de consistência.
Builds utilizadas em diferentes partidas.
Identificação de padrões associados a melhores resultados.

Visualizações previstas:

Perfil analítico do jogador.
Histórico de desempenho.
Comparação entre heróis.
Indicadores por período.
Relatório resumido de desempenho.

O módulo dependerá da disponibilidade dos dados e das permissões ou limitações de consulta aplicáveis a cada endpoint.

Módulo 4 — Análise de partidas e jogadores

Objetivo: investigar os fatores associados aos resultados das partidas.

Funcionalidades previstas:

Consulta de partidas.
Detalhes e composição das equipes.
Comparação entre jogadores.
Estatísticas individuais e coletivas.
Relação entre duração e resultado.
Análise de confrontos entre heróis.
Relação entre itens, composição e resultado.
Eventos temporais, caso os dados estejam disponíveis.
Histórico de confrontos, quando suportado pelos dados.

Visualizações previstas:

Detalhamento analítico de uma partida.
Comparação entre equipes.
Tabelas de jogadores.
Linha do tempo de eventos.
Comparação entre partidas. 3. Tecnologias
Stack inicial
Tecnologia Responsabilidade
Python Linguagem principal
Requests Consumo da API HTTP
Pandas Transformação e análise de dados
PostgreSQL Banco de dados relacional
SQL Consultas e cálculos analíticos
SQLAlchemy ou psycopg Integração Python/PostgreSQL
Streamlit Aplicação web analítica
Plotly Gráficos interativos
Git e GitHub Versionamento e portfólio
Pytest Testes automatizados
Tecnologias futuras

Adicionar somente quando houver uma necessidade concreta:

DuckDB para explorar arquivos Parquet.
dbt para organizar transformações SQL.
Prefect ou Airflow para orquestração.
Docker para padronizar o ambiente.
CI para executar testes automaticamente.
Serviços de cloud para publicação e armazenamento.

Decisão inicial: desenvolver localmente, com Python, PostgreSQL e Streamlit. Evitar complexidade de infraestrutura antes de existir um pipeline funcional.

4. Arquitetura proposta

O projeto seguirá um fluxo de dados em camadas:

Deadlock API / Data Dumps
|
v
Ingestão Python
|
v
Dados brutos (raw)
|
v
Transformação e validação
|
v
PostgreSQL
|
v
Consultas SQL
|
v
Camada analítica Python
|
v
Streamlit + Plotly
|
v
Usuário final

Responsabilidades das camadas

Ingestão

Fazer requisições HTTP.
Controlar parâmetros e paginação.
Tratar erros de comunicação.
Respeitar limites de requisições.
Registrar a execução da coleta.

Dados brutos

Preservar respostas originais quando apropriado.
Permitir inspeção e reprodução das transformações.
Registrar datas de coleta.
Evitar sobrescrever históricos importantes sem necessidade.

Transformação

Padronizar nomes e tipos de campos.
Tratar valores ausentes.
Deduplicar registros.
Validar chaves e relacionamentos.
Preparar os dados para o modelo relacional.

Persistência

Armazenar entidades e fatos no PostgreSQL.
Definir chaves primárias e estrangeiras.
Implementar cargas repetíveis.
Manter histórico quando necessário.

Camada analítica

Calcular indicadores.
Disponibilizar consultas reutilizáveis.
Separar regras de negócio da interface.
Validar a consistência dos resultados.

Apresentação

Exibir filtros, tabelas e gráficos.
Permitir explorar heróis, itens, jogadores e partidas.
Informar o período e a quantidade de observações das análises. 5. Estrutura de diretórios

A estrutura evoluirá à medida que o projeto crescer.

deadlock-analytics/
├── README.md
├── ROADMAP.md
├── requirements.txt
├── .gitignore
├── .env.example
│
├── data/
│ ├── raw/
│ ├── processed/
│ └── samples/
│
├── sql/
│ ├── ddl/
│ ├── staging/
│ └── analytics/
│
├── src/
│ └── deadlock_analytics/
│ ├── **init**.py
│ ├── config.py
│ │
│ ├── ingestion/
│ │ ├── **init**.py
│ │ ├── client.py
│ │ └── heroes.py
│ │
│ ├── transformations/
│ │ ├── **init**.py
│ │ └── heroes.py
│ │
│ ├── database/
│ │ ├── **init**.py
│ │ └── connection.py
│ │
│ ├── analytics/
│ │ ├── **init**.py
│ │ ├── hero_stats.py
│ │ ├── item_stats.py
│ │ ├── player_stats.py
│ │ └── match_stats.py
│ │
│ └── pipelines/
│ ├── **init**.py
│ └── ingest_heroes.py
│
├── app/
│ ├── Home.py
│ └── pages/
│ ├── 01_Heroes.py
│ ├── 02_Items_Builds.py
│ ├── 03_Player_Performance.py
│ └── 04_Match_Analysis.py
│
└── tests/
├── test_api_client.py
├── test_heroes.py
└── test_analytics.py

Essa estrutura é o destino planejado, não algo que precisa ser criado inteiro no primeiro dia.

Os módulos serão adicionados conforme suas responsabilidades forem surgindo. Isso evita criar arquivos vazios e abstrações que ainda não resolvem problemas reais.

Os diretórios data/ e os arquivos .env não deverão ser enviados ao Git por padrão. Amostras pequenas, públicas e sanitizadas poderão ser versionadas deliberadamente.

6. Modelo de dados inicial

O esquema será definido após inspecionar os endpoints reais e suas respostas.

Dimensões propostas
Tabela Descrição
dim_heroes Cadastro de heróis
dim_items Cadastro de itens
dim_players Identificadores dos jogadores
dim_patches Versões do jogo e referências temporais
dim_dates Calendário analítico, se necessário
Tabelas de fatos propostas
Tabela Granularidade
fact_matches Uma linha por partida
fact_player_matches Um jogador em uma partida
fact_item_purchases Uma compra de item
fact_ability_upgrades Uma evolução de habilidade
fact_match_events Um evento de partida

Essas tabelas representam uma proposta de modelagem, e não necessariamente tabelas já existentes na API.

Regras de modelagem
Definir a granularidade antes de criar cada tabela.
Utilizar identificadores estáveis.
Definir chaves primárias e estrangeiras.
Evitar duplicação de atributos descritivos.
Registrar datas e versões de referência.
Distinguir dados desconhecidos de valores iguais a zero.
Preservar a origem dos dados quando necessário.
Criar índices com base nas consultas reais.
Utilizar restrições de unicidade para impedir duplicações.

A implementação começará com as entidades necessárias ao primeiro módulo. As tabelas de compras, eventos e histórico só serão criadas quando os respectivos dados forem confirmados.

7. Roadmap de desenvolvimento

As estimativas abaixo são indicativas para desenvolvimento individual em ritmo parcial. O tempo real dependerá da disponibilidade dos dados e das dificuldades encontradas.

Fase 0 — Exploração e planejamento

Estimativa: 1–2 sessões.

Consultar a documentação oficial.
Identificar endpoints de heróis e estatísticas agregadas.
Fazer requisições de teste.
Inspecionar exemplos reais de respostas JSON.
Verificar parâmetros, filtros, paginação e limites.
Identificar quais dados podem ser consultados historicamente.
Registrar os campos necessários para o primeiro módulo.

Entregável: inventário inicial de endpoints e campos.

Critério de conclusão: saber quais dados são necessários para o dashboard inicial e como obtê-los.

Fase 1 — Estrutura do projeto e primeiro coletor

Estimativa: 2–4 sessões.

Criar o repositório.
Configurar o ambiente virtual.
Criar requirements.txt.
Criar a estrutura inicial de pastas.
Implementar o cliente HTTP.
Consultar o endpoint de heróis.
Salvar a resposta em JSON.
Implementar tratamento de erros.
Registrar informações básicas da execução.

Entregável: primeiro programa funcional de ingestão.

Critério de conclusão: conseguir executar o programa e salvar a resposta sem depender do diretório de trabalho do terminal.

Fase 2 — PostgreSQL e persistência

Estimativa: 3–5 sessões.

Configurar uma base PostgreSQL local.
Configurar as credenciais fora do código.
Criar a primeira tabela de heróis.
Definir chaves e tipos de dados.
Implementar a carga dos dados.
Evitar registros duplicados.
Implementar atualização dos registros.
Validar a persistência com SQL.
Documentar como reproduzir a carga.

Entregável: dados de heróis disponíveis no PostgreSQL.

Critério de conclusão: executar a carga repetidamente sem gerar duplicações indevidas.

Fase 3 — Pipeline de ingestão e qualidade

Estimativa: 3–5 sessões.

Separar cliente HTTP e coletores específicos.
Separar coleta e transformação.
Implementar validações de esquema.
Tratar campos ausentes e tipos inesperados.
Adicionar logs.
Registrar início, fim e resultado das execuções.
Implementar retentativas limitadas para erros transitórios.
Testar respostas vazias e erros HTTP.
Documentar o processo de atualização.

Entregável: pipeline reutilizável e minimamente confiável.

Critério de conclusão: falhas podem ser identificadas e diagnosticadas sem precisar investigar manualmente todo o código.

Fase 4 — Dashboard do meta

Estimativa: 4–7 sessões.

Identificar os endpoints de estatísticas agregadas.
Confirmar a definição dos indicadores fornecidos.
Criar consultas analíticas.
Calcular ou validar win rate.
Calcular ou validar pick rate.
Exibir o número de partidas por herói.
Implementar filtros por rank, patch e período quando disponíveis.
Criar rankings e gráficos.
Adicionar comparação entre heróis.
Validar os resultados com exemplos da API.

Entregável: primeiro dashboard funcional.

Critério de conclusão: o usuário consegue explorar e comparar heróis com indicadores e filtros coerentes.

Fase 5 — Análise de itens e builds

Estimativa: 4–7 sessões, após confirmar a granularidade dos dados.

Identificar os endpoints de itens e estatísticas de builds.
Verificar se há dados de compras individuais ou apenas agregados.
Definir formalmente o que caracteriza uma build.
Criar as tabelas e transformações necessárias.
Calcular frequência e win rate associados aos itens.
Comparar builds para o mesmo herói.
Considerar rank, patch e período.
Exibir quantidade de observações.
Investigar combinações de itens.
Avaliar a incerteza estatística dos resultados.

Entregável: módulo de comparação de itens e builds.

Critério de conclusão: o usuário consegue comparar alternativas sem confundir frequência, associação estatística e causalidade.

Fase 6 — Desempenho pessoal

Estimativa: 3–6 sessões, dependendo dos endpoints disponíveis.

Implementar consultas de jogadores.
Obter histórico de partidas.
Consolidar os indicadores por jogador.
Analisar resultados por herói.
Comparar períodos.
Implementar gráficos temporais.
Identificar limitações de histórico e cobertura.
Criar a interface de consulta individual.

Entregável: perfil analítico de jogador.

Critério de conclusão: consultar um jogador e obter uma visão consistente do seu histórico disponível.

Fase 7 — Análise de partidas

Estimativa: 4–8 sessões, dependendo da disponibilidade de dados detalhados.

Consultar metadados das partidas.
Relacionar partidas, jogadores e heróis.
Comparar equipes.
Analisar duração e resultado.
Integrar dados de itens, quando disponíveis.
Avaliar eventos temporais.
Construir o detalhamento analítico da partida.
Validar a integridade dos relacionamentos.

Entregável: módulo de análise de partidas e jogadores.

Critério de conclusão: consultar uma partida e explorar as informações efetivamente disponíveis sobre sua composição e seu resultado.

Fase 8 — Testes, documentação e publicação

Estimativa: 3–6 sessões.

Criar testes unitários para transformações.
Criar testes para o cliente HTTP.
Testar as consultas analíticas.
Criar dados de teste reproduzíveis.
Documentar a configuração local.
Documentar o modelo de dados.
Criar um README com exemplos e capturas de tela.
Configurar execução automatizada de testes.
Publicar o dashboard, se desejado.
Revisar segurança e configuração de credenciais.

Entregável: projeto documentado e apresentável para portfólio.

Critério de conclusão: outra pessoa consegue configurar o ambiente, executar os testes e compreender a arquitetura.

8. Indicadores e definições analíticas

As métricas deverão ser documentadas para que seus significados não mudem entre módulos.

Indicador Definição
Win rate Vitórias divididas pelo número de partidas elegíveis
Pick rate Participações ou escolhas do herói divididas pelo total de oportunidades elegíveis, conforme a definição da fonte
Frequência de item Quantidade de ocorrências de compra ou uso, conforme os dados disponíveis
Win rate associado a item Vitórias divididas pelas partidas elegíveis que correspondem à definição do item
Desempenho por herói Métricas do jogador segmentadas por herói
Evolução temporal Variação de uma métrica ao longo de intervalos definidos
Consistência Variabilidade de métricas comparáveis entre partidas
Cuidados estatísticos
Informar o tamanho da amostra.
Evitar rankings baseados apenas em percentuais.
Utilizar intervalos de confiança quando apropriado.
Comparar períodos e patches compatíveis.
Considerar diferenças entre faixas de rank.
Evitar misturar métricas com definições distintas.
Evitar vazamento de informações futuras em modelos preditivos.
Documentar filtros e critérios de inclusão. 9. Boas práticas de engenharia
Código
Utilizar funções com responsabilidades claras.
Evitar funções excessivamente longas.
Separar lógica de negócio de entrada e saída.
Utilizar nomes explícitos.
Evitar duplicar transformações.
Configurar caminhos e credenciais fora da lógica principal.
Adicionar anotações de tipos quando forem úteis.
Banco de dados
Definir chaves primárias e estrangeiras.
Utilizar transações quando apropriado.
Criar restrições de unicidade.
Separar dados brutos de dados analíticos quando necessário.
Versionar alterações no esquema.
Evitar executar consultas pesadas repetidamente sem necessidade.
API
Respeitar limites de requisição.
Configurar timeouts.
Tratar erros transitórios e permanentes de forma diferente.
Registrar falhas.
Evitar requisições repetidas desnecessárias.
Validar a resposta antes de persistir os dados.
Git
Fazer commits pequenos e descritivos.
Manter o main em condição funcional.
Não versionar credenciais.
Documentar mudanças relevantes.
Criar uma amostra sanitizada para testes quando possível. 10. Estratégia de testes

Os testes serão introduzidos progressivamente.

Testes unitários

Validar funções de transformação usando dados pequenos e conhecidos.

Exemplos:

Calcular win rate corretamente.
Tratar valores ausentes.
Deduplicar registros.
Normalizar tipos.
Classificar builds conforme a definição escolhida.
Testes de integração

Validar a interação entre os componentes:

Cliente HTTP e tratamento da resposta.
Transformação e persistência.
Inserção e atualização no PostgreSQL.
Consultas analíticas.
Testes de qualidade

Verificar:

Chaves únicas.
Relacionamentos válidos.
Campos obrigatórios.
Datas coerentes.
Contagens de registros.
Percentuais dentro dos limites esperados.
Consistência entre resultados calculados em Python e SQL.

Os testes da API deverão utilizar respostas simuladas sempre que possível, evitando dependência de disponibilidade externa.

11. Organização do aprendizado

O projeto também será utilizado como trilha prática de aprendizagem.

Tema Aplicação prática
Organização de código Separar coletores, transformações e análises
APIs HTTP Fazer requisições e tratar erros
JSON Inspecionar e normalizar respostas
Pandas Limpar, agrupar e validar dados
SQL Criar consultas analíticas
PostgreSQL Persistir e relacionar entidades
Modelagem dimensional Organizar fatos e dimensões
Estatística Avaliar métricas e incerteza
Testes Verificar comportamento esperado
Git Registrar a evolução do projeto
Streamlit Criar uma aplicação interativa
Documentação Tornar o projeto reproduzível

A regra será aprender um conceito quando ele se tornar necessário para a próxima entrega.

12. Gestão das tarefas

Cada tarefa deverá possuir:

Objetivo: o que será implementado.
Motivação: por que a funcionalidade é necessária.
Entradas: quais dados serão utilizados.
Saídas: o que deverá ser produzido.
Validação: como saber se funcionou.
Documentação: o que precisa ser registrado.
Definition of Done

Uma tarefa será considerada concluída quando:

O comportamento esperado estiver implementado.
O resultado tiver sido validado.
Erros relevantes estiverem tratados.
Os testes aplicáveis estiverem passando.
A documentação necessária estiver atualizada.
O código estiver versionado. 13. Primeiras tarefas executáveis

A prioridade imediata é criar uma primeira entrega pequena, sem antecipar toda a arquitetura.

Criar o diretório deadlock-analytics.
Inicializar o repositório Git.
Criar e ativar o ambiente virtual.
Instalar requests.
Criar src/main.py.
Consultar GET /v1/assets/heroes.
Inspecionar a resposta real.
Salvar a resposta em data/raw/.
Registrar os campos observados.
Documentar como executar o programa.

Primeiro marco: conseguir obter e inspecionar os dados dos heróis de forma reproduzível.

Segundo marco: carregar esses dados no PostgreSQL.

Terceiro marco: construir o primeiro dashboard do meta.

Só depois de validar esses marcos o escopo será expandido.

14. Riscos e dependências
    Disponibilidade dos dados

Nem todos os endpoints necessariamente disponibilizam o mesmo nível de detalhe. Antes de planejar análises de compras, eventos ou histórico, verificar a documentação e exemplos reais.

Mudanças na API

Endpoints, campos e parâmetros podem mudar. O código deverá validar respostas e evitar assumir esquemas imutáveis.

Cobertura histórica

Uma estatística agregada atual não garante que seja possível reconstruir seu histórico passado. A coleta periódica poderá ser necessária para construir séries temporais próprias.

Limites e desempenho

A coleta deverá respeitar limites de requisições, utilizar paginação quando necessário e evitar consultas desnecessárias.

Interpretação dos resultados

Indicadores observacionais não demonstram causalidade. O contexto da partida e a seleção dos jogadores podem influenciar os resultados.

15. Critérios de sucesso do projeto

O projeto será considerado bem-sucedido quando:

A ingestão funcionar de forma reproduzível.
Os dados estiverem armazenados no PostgreSQL.
As transformações forem testáveis.
O dashboard do meta permitir comparar heróis.
O módulo de itens permitir analisar itens e builds com amostras explícitas.
O módulo de jogadores apresentar o histórico disponível.
O módulo de partidas relacionar corretamente jogadores, equipes e resultados.
A documentação permitir reproduzir a execução.
Os principais cálculos tiverem definições documentadas.
O repositório estiver organizado e pronto para demonstração. 16. Links de referência
Deadlock API — site principal
Documentação interativa da API
Data dumps

A documentação oficial deverá ser a referência para confirmar endpoints, parâmetros, limites e formatos de resposta durante cada etapa.

Resumo executivo

O Deadlock Analytics será construído em quatro grandes blocos:

Ingestão e persistência: coletar os dados e armazená-los corretamente.
Análise do meta: transformar dados em indicadores de heróis.
Análise competitiva: investigar itens, builds, jogadores e partidas.
Aplicação e qualidade: disponibilizar os resultados em dashboards e tornar o projeto reproduzível.

A prioridade inicial não é construir a plataforma inteira, mas estabelecer um fluxo confiável entre a API, Python e PostgreSQL. A partir desse fundamento, cada novo módulo poderá ser desenvolvido sem precisar reconstruir o projeto.

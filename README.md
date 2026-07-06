# Grupo 03

Projeto: Investigacao do Desperdicio de Alimentos em Servicos de Buffet.

Integrantes: Arthur Provenzi Parizotto, Bianca Maia Ribeiro, Emilly Nascimento
Dias e Rafael Jacques do Nascimento Lopes.

## Status do projeto

Em andamento no momento: **Parte 1** (analise estatistica) e **Parte 2**
(dashboard Streamlit). A **Parte 3** (organizacao das camadas de dados
bronze/silver/gold, validacao da camada gold e documentacao dos indicadores)
ja foi realizada. A Parte 4 (Dockerfile, compose.yaml e documentacao final de
reprodutibilidade) ainda nao foi iniciada. Ver `DIVISAO_RESPONSABILIDADES.md`
para o detalhamento de cada parte.

A base `data/gold/food_wastage_gold.csv` incluida no repositorio permite a
execucao local da analise e do dashboard sem etapa de download. A estrutura
de camadas (bronze/silver/gold) e a validacao da camada gold estao descritas
na secao *Dados e indicadores (Parte 3)*.

## Analise estatistica (Parte 1)

Script que valida as hipoteses exploratorias (HE-01 a HE-06) com testes
estatisticos formais: teste t de Welch, Kruskal-Wallis, bootstrap de
intervalo de confianca e correlacao de Pearson/Spearman.

```
analysis/
  analise_estatistica.py   # python analysis/analise_estatistica.py
```

### Como executar

```bash
pip install -r requirements.txt
python analysis/analise_estatistica.py
```

Por padrao le `data/gold/food_wastage_gold.csv` e gera em
`outputs/analise/`:

- `resumo_analises.csv` - estimativa, IC 95%, p-valor e tamanho de efeito por analise.
- `estatisticas_grupos.csv` - estatisticas descritivas por grupo.
- `perfis_risco.csv` - ranking de perfis operacionais por taxa media de desperdicio.
- `relatorio_analise.md` - relatorio consolidado em markdown.

## Dados e indicadores (Parte 3)

Organizacao das camadas de dados e validacao da camada gold que sustenta o
dashboard e a analise.

### Estrutura das camadas

```
data/
  bronze/   # dados crus, como recebidos da fonte (ver data/bronze/README.md)
  silver/   # dados limpos e padronizados (ver data/silver/README.md)
  gold/
    food_wastage_gold.csv   # base final com indicadores, usada pelo app e pela analise
```

Todos os caminhos de dados sao relativos (resolvidos a partir da raiz do
repositorio), compativeis com execucao local e via Docker.

### Validacao da camada gold

```bash
python analysis/validacao_camada_gold.py
```

Confere colunas obrigatorias, valores ausentes, duplicatas, consistencia
logica e as formulas dos indicadores. Termina com codigo `0` se a camada gold
estiver valida. O resultado detalhado esta em
`docs/checklist_validacao_gold.md`.

### Dicionario de indicadores

As definicoes e formulas dos indicadores (`wastage_rate`,
`wastage_per_guest`, `event_profile`, `waste_risk_rank`, entre outros) estao
em `docs/dicionario_indicadores.md`. Principais formulas:

- `wastage_rate = wastage_food_amount / quantity_of_food * 100`
- `wastage_per_guest = wastage_food_amount / number_of_guests`
- `waste_risk_rank`: ranking do `event_profile` pela taxa media de
  desperdicio, em ordem decrescente (1 = maior risco).

## Dashboard Streamlit (Parte 2)

Aplicacao interativa que consolida o pipeline do projeto (contexto, dados,
indicadores, analises por pergunta e conclusoes) em `http://localhost:8501`.

### Estrutura

```
app/
  app.py                     # ponto de entrada (streamlit run app/app.py)
  components/
    filters.py               # filtros da barra lateral
    indicators.py            # calculo e exibicao dos indicadores (KPIs)
    charts.py                 # construtores de graficos Plotly (box/violin,
                               # barras, heatmap, ranking, scatter)
  services/
    data.py                   # carregamento da camada gold, filtragem e
                               # ranking de perfis de risco
  utils/
    formatting.py             # formatacao de percentuais e numeros
data/
  gold/food_wastage_gold.csv  # base gold usada pelo dashboard e pela analise
```

### Como executar localmente

```bash
pip install -r requirements.txt
streamlit run app/app.py
```

Acesse `http://localhost:8501`. Para encerrar, use `Ctrl+C` no terminal.

### Navegacao

- **Contexto e problema** - problema do desperdicio, perguntas Q1-Q4 e
  amostra da base gold.
- **Indicadores gerais** - taxa media de desperdicio, desperdicio medio por
  evento, desperdicio por convidado, quantidade media produzida, perfil de
  maior risco e maior diferenca entre grupos, para a selecao atual de filtros.
- **Analises por pergunta** - uma aba por pergunta (Q1 a Q4), cada uma com o
  grafico mais adequado (boxplot/violin, barras, heatmap, scatter ou ranking)
  e um texto curto de interpretacao.
- **Perfis de risco** - ranking completo dos perfis operacionais
  (`event_size | preparation_method | pricing`) por taxa media de
  desperdicio, com tabela detalhada.
- **Conclusoes e limitacoes** - situacao de cada hipotese avaliada
  (confirmada, rejeitada ou parcialmente confirmada) e cuidados de
  interpretacao (dados observacionais, perfis com poucos eventos, etc.).

### Controles (filtros)

Na barra lateral, valem para todas as paginas exceto "Contexto e problema":

- Metodo de preparo (`preparation_method`)
- Faixa de preco / pricing (`pricing`)
- Tipo de evento (`event_type`)
- Tipo de alimento (`type_of_food`)
- Porte do evento (`event_size`)
- Condicao de armazenamento (`storage_conditions`)

Todos os filtros iniciam com todas as opcoes selecionadas (nenhum filtro
vazio na abertura). O botao "Limpar filtros" restaura essa selecao completa.

## Repositorio

```bash
git clone https://gitlab.unipampa.edu.br/ales/icd-2026.1/grupo-03.git
```

# Grupo 03

Projeto: Investigacao do Desperdicio de Alimentos em Servicos de Buffet.

Integrantes: Arthur Provenzi Parizotto, Bianca Maia Ribeiro, Emilly Nascimento
Dias e Rafael Jacques do Nascimento Lopes.

## Status do projeto

Em andamento no momento: **Parte 1** (analise estatistica) e **Parte 2**
(dashboard Streamlit). As Partes 3 (organizacao completa das camadas de dados
bronze/silver/gold e validacao) e 4 (Dockerfile, compose.yaml e documentacao
final de reprodutibilidade) ainda nao foram iniciadas. Ver
`DIVISAO_RESPONSABILIDADES.md` para o detalhamento de cada parte.

A base `data/gold/food_wastage_gold.csv` incluida no repositorio e um
adiantamento necessario para permitir a execucao local da analise e do
dashboard; a organizacao definitiva das camadas de dados (bronze/silver/gold)
e a validacao completa dela sao responsabilidade da Parte 3.

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

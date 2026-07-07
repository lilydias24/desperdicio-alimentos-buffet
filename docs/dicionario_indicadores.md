# Dicionario de indicadores - camada gold

Parte 3 - Dados, indicadores e rastreabilidade do pipeline.

Este dicionario descreve as colunas da camada gold
(`data/gold/food_wastage_gold.csv`) usadas pelo dashboard e pela analise.
As formulas foram conferidas pelo script `analysis/validacao_camada_gold.py`.

## Unidade de analise

Cada linha da camada gold representa **um registro/evento operacional de
desperdicio de alimentos** (um preparo/servico associado a um evento). A
gold nao e uma tabela agregada por categoria: e uma base em nivel de
evento, enriquecida com indicadores, classificacoes e rankings. Fonte:
Kaggle, dataset "Food Wastage Data in Restaurant"
(<https://www.kaggle.com/datasets/trevinhannibal/food-wastage-data-in-restaurant>).

## Variaveis de base

| Coluna | Descricao | Tipo |
|---|---|---|
| `type_of_food` | Tipo de alimento servido no evento. | categorica |
| `event_type` | Tipo de evento (ex.: Corporate, Birthday, Wedding). | categorica |
| `number_of_guests` | Numero de convidados do evento. | numerica (> 0) |
| `quantity_of_food` | Quantidade de alimento produzida. **Unidade nao declarada pela fonte original** (assume-se quilogramas por convencao do grupo; ver limitacao abaixo). | numerica (> 0) |
| `wastage_food_amount` | Quantidade de alimento desperdicada, na mesma unidade assumida de `quantity_of_food`. | numerica (>= 0) |
| `preparation_method` | Metodo de preparo (ex.: Buffet, Sit-down Dinner, Finger Food). | categorica |
| `storage_conditions` | Condicao de armazenamento (ex.: Refrigerated, Room Temperature). | categorica |
| `pricing` | Faixa de preco do evento (Low, Moderate, High). | categorica |
| `purchase_history` | Historico de compra do evento (`Regular` ou `Occasional`). Nao usada nos filtros/graficos do dashboard: o significado operacional exato (ex.: frequencia de compra do cliente vs. do fornecedor) nao e explicitado pela fonte. | categorica |
| `seasonality` | Estacao associada ao evento (`Summer`, `Winter`, `All Seasons`). Nao usada nos filtros/graficos do dashboard: a fonte nao especifica se representa estacao climatica, sazonalidade do alimento ou periodo do evento. | categorica |
| `geographical_location` | Localizacao do evento (`Urban`, `Suburban`, `Rural`). Nao usada nos filtros/graficos do dashboard. | categorica |

## Indicadores derivados

| Indicador | Formula / definicao | Unidade |
|---|---|---|
| `wastage_rate` | `wastage_food_amount / quantity_of_food * 100` | % (ponto percentual) |
| `wastage_per_guest` | `wastage_food_amount / number_of_guests` | por convidado |
| `event_size` | Porte do evento derivado de `number_of_guests` (ex.: Pequeno, Medio, Grande). | categorica ordinal |
| `quantity_tier` | Faixa de quantidade produzida derivada de `quantity_of_food` (ex.: Baixa, Media, Alta). | categorica ordinal |
| `event_profile` | Perfil operacional que combina `event_size \| preparation_method \| pricing`. | categorica |
| `waste_risk_rank` | Ranking do `event_profile` pela taxa media de desperdicio, em ordem decrescente (1 = maior risco). | inteiro (1 = pior) |
| `storage_inadequate` | `True` quando `storage_conditions == "Room Temperature"`. Nao usada diretamente no dashboard (o filtro usa `storage_conditions`). | booleana |
| `mean_wastage_by_prep_method` | Media de `wastage_food_amount` por `preparation_method`, calculada sobre toda a base e atribuida a cada linha do grupo. | numerica |
| `mean_wastage_rate_by_food_type` | Media de `wastage_rate` por `type_of_food`, calculada sobre toda a base. | % |
| `mean_wastage_rate_by_profile` | Media de `wastage_rate` por `event_profile`, calculada sobre toda a base (equivalente a coluna auxiliar do `waste_risk_rank`). | % |

**Cautela sobre as colunas `mean_wastage_*`:** foram calculadas sobre toda
a base (nao apenas um conjunto de treino). Sao adequadas para a analise
descritiva/exploratoria deste projeto, mas **nao devem ser usadas como
features em modelagem preditiva futura sem recalculo restrito ao conjunto
de treino**, sob risco de vazamento de informacao (data leakage). Essa
mesma ressalva esta documentada em `notebooks/2_transformation.ipynb`
(secao "Limitacoes da Transformacao Realizada").

## Indicadores calculados no dashboard

Alem das colunas acima, o dashboard calcula, sobre a selecao de filtros ativa:

| Indicador (KPI) | Definicao |
|---|---|
| Taxa media de desperdicio | Media de `wastage_rate`. |
| Desperdicio medio por evento | Media de `wastage_food_amount`. |
| Desperdicio por convidado | Media de `wastage_per_guest`. |
| Quantidade media produzida | Media de `quantity_of_food`. |
| Perfil de maior risco | `event_profile` com maior taxa media de desperdicio. |
| Maior diferenca entre grupos | Maior diferenca de media de `wastage_rate` entre categorias (por padrao, `preparation_method`), considerando apenas grupos com contagem suficiente. |

## Observacoes de interpretacao

- Os indicadores mudam conforme os filtros aplicados no dashboard; comparacoes
  entre paginas so sao validas com os mesmos filtros ativos.
- Perfis (`event_profile`) com poucos eventos tem media instavel; o ranking
  `waste_risk_rank` deve ser lido junto com o numero de eventos de cada perfil.
- O dataset e observacional: os indicadores descrevem associacoes, nao
  relacoes de causa e efeito.
- A unidade de `quantity_of_food` e `wastage_food_amount` (assumida como
  quilogramas) e uma inferencia do grupo, nao uma confirmacao da fonte
  original (ver `data/bronze/README.md`).
- `purchase_history`, `seasonality` e `geographical_location` estao
  presentes na base gold mas tem definicao operacional ambigua na fonte
  original; por isso nao sao usadas como filtros ou variaveis de analise
  no dashboard.

# Dicionario de indicadores - camada gold

Parte 3 - Dados, indicadores e rastreabilidade do pipeline.

Este dicionario descreve as colunas da camada gold
(`data/gold/food_wastage_gold.csv`) usadas pelo dashboard e pela analise.
As formulas foram conferidas pelo script `analysis/validacao_camada_gold.py`.

## Variaveis de base

| Coluna | Descricao | Tipo |
|---|---|---|
| `type_of_food` | Tipo de alimento servido no evento. | categorica |
| `event_type` | Tipo de evento (ex.: Corporate, Birthday, Wedding). | categorica |
| `number_of_guests` | Numero de convidados do evento. | numerica (> 0) |
| `quantity_of_food` | Quantidade de alimento produzida. | numerica (> 0) |
| `wastage_food_amount` | Quantidade de alimento desperdicada. | numerica (>= 0) |
| `preparation_method` | Metodo de preparo (ex.: Buffet, Sit-down Dinner, Finger Food). | categorica |
| `storage_conditions` | Condicao de armazenamento (ex.: Refrigerated, Room Temperature). | categorica |
| `pricing` | Faixa de preco do evento (Low, Moderate, High). | categorica |

## Indicadores derivados

| Indicador | Formula / definicao | Unidade |
|---|---|---|
| `wastage_rate` | `wastage_food_amount / quantity_of_food * 100` | % (ponto percentual) |
| `wastage_per_guest` | `wastage_food_amount / number_of_guests` | por convidado |
| `event_size` | Porte do evento derivado de `number_of_guests` (ex.: Pequeno, Medio, Grande). | categorica ordinal |
| `quantity_tier` | Faixa de quantidade produzida derivada de `quantity_of_food` (ex.: Baixa, Media, Alta). | categorica ordinal |
| `event_profile` | Perfil operacional que combina `event_size \| preparation_method \| pricing`. | categorica |
| `waste_risk_rank` | Ranking do `event_profile` pela taxa media de desperdicio, em ordem decrescente (1 = maior risco). | inteiro (1 = pior) |

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

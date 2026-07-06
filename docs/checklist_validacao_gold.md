# Checklist de validacao da camada gold

Parte 3 - Dados, indicadores e rastreabilidade do pipeline.

Base validada: `data/gold/food_wastage_gold.csv` (1618 linhas, 21 colunas).

A validacao e reproduzida pelo script `analysis/validacao_camada_gold.py`:

```bash
python analysis/validacao_camada_gold.py
```

O script termina com codigo `0` quando todas as verificacoes criticas passam
e `1` caso contrario. A tolerancia usada para comparar indicadores
recalculados e de `0.01`, porque a base gold armazena os indicadores
arredondados em 4 casas decimais.

## Estrutura de dados

- [x] Existe a pasta `data/bronze/`.
- [x] Existe a pasta `data/silver/`.
- [x] Existe a pasta `data/gold/`.
- [x] `food_wastage_gold.csv` esta em `data/gold/`.
- [x] Todos os caminhos de dados sao relativos (resolvidos a partir da raiz
      do repositorio), compativeis com execucao local e via Docker.

## Colunas obrigatorias

Todas as 14 colunas exigidas pela Parte 3 estao presentes:

- [x] `type_of_food`
- [x] `event_type`
- [x] `number_of_guests`
- [x] `quantity_of_food`
- [x] `wastage_food_amount`
- [x] `preparation_method`
- [x] `storage_conditions`
- [x] `pricing`
- [x] `wastage_rate`
- [x] `wastage_per_guest`
- [x] `event_size`
- [x] `quantity_tier`
- [x] `event_profile`
- [x] `waste_risk_rank`

## Qualidade dos dados

- [x] Valores ausentes nas colunas obrigatorias: **0**.
- [x] Linhas duplicadas: **0**.
- [x] `quantity_of_food > 0` em todas as linhas (0 invalidas).
- [x] `number_of_guests > 0` em todas as linhas (0 invalidas).
- [x] `wastage_food_amount >= 0` em todas as linhas (0 invalidas).
- [x] `wastage_food_amount <= quantity_of_food` em todas as linhas (0 invalidas).

## Indicadores

- [x] `wastage_rate = wastage_food_amount / quantity_of_food * 100`
      (maior diferenca observada: ~0,00005 p.p., dentro da tolerancia).
- [x] `wastage_per_guest = wastage_food_amount / number_of_guests`
      (maior diferenca observada: ~0,00005, dentro da tolerancia).
- [x] `mean_wastage_rate_by_profile` corresponde a media de `wastage_rate`
      por `event_profile` (coluna auxiliar; maior diferenca ~0,00005).
- [x] `waste_risk_rank` corresponde ao ranking decrescente da taxa media de
      desperdicio por perfil (1 = maior risco), com 26 perfis distintos.

## Comparacao com a AED / analise do projeto

Os numeros abaixo, recalculados a partir da base gold, batem com os achados
jacitados no dashboard (`app/app.py`) e na etapa de analise
(`analysis/analise_estatistica.py`):

- [x] Perfil de maior risco (`waste_risk_rank = 1`):
      **Pequeno | Sit-down Dinner | High**, com taxa media ~11,14%
      (amostra pequena, ler com cautela).
- [x] 2o e 3o perfis de maior risco: **Medio | Sit-down Dinner | High**
      (~9,10%) e **Grande | Sit-down Dinner | High** (~9,00%).
- [x] Numero de perfis operacionais distintos: **26**.

## Observacoes

- As pastas `data/bronze/` e `data/silver/` estao versionadas (via arquivo
  `README.md` em cada uma), mas ainda sem arquivos de dados. A base gold e
  incluida diretamente no repositorio para permitir execucao local e via
  Docker sem etapa de download.
- Nenhum ajuste foi necessario nos dados: a camada gold ja estava consistente
  com as formulas dos indicadores e com as regras de consistencia logica.
- A base tem origem sintetica/educacional (Kaggle); os valores servem para
  ilustrar o metodo e nao devem ser generalizados para operacoes reais.

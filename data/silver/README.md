# Camada silver

Camada de dados **limpos e padronizados**: tipos corrigidos, colunas
normalizadas e duplicatas completas removidas a partir da camada bronze,
ainda sem os indicadores finais de negocio.

## Arquivo

- `food_wastage_silver.csv` - **1618 linhas x 11 colunas** (mesmas colunas
  da bronze, renomeadas para `snake_case`).

## Transformacoes aplicadas

1. **Padronizacao de nomes de colunas** para `snake_case` (ex.:
   `Type of Food` -> `type_of_food`).
2. **Conversao de tipos**: colunas categoricas convertidas para o tipo
   `category`.
3. **Verificacao de valores ausentes**: nenhum valor ausente encontrado
   (0 intervencoes necessarias).
4. **Verificacao de inconsistencia logica** (`wastage_food_amount >
   quantity_of_food`, valores <= 0 em colunas numericas): nenhuma
   inconsistencia encontrada (0 linhas removidas por este criterio).
5. **Remocao de duplicatas completas**: removidas **164 linhas**
   idênticas em todas as 11 colunas originais (mantida a primeira
   ocorrencia, `keep='first'`). Esse foi o **unico** criterio que reduziu
   o dataset, de 1782 (bronze) para 1618 (silver) linhas.

Como o dataset nao possui identificador unico por evento, a duplicidade
considerada e apenas a **duplicidade completa** (linha inteira repetida).
Esse criterio e conservador: nao remove registros parecidos, so remove
registros exatamente iguais. Ainda assim, sem chave primaria, nao e
possivel provar com certeza se uma linha identica repetida e um erro de
registro ou um evento real coincidente.

## Reproducao

Os passos acima estao documentados e executaveis em
`notebooks/1_cleaning.ipynb`. O arquivo `food_wastage_silver.csv` deste
repositorio foi gerado reproduzindo exatamente essa logica (mesmos
totais: 1782 -> 1618, 164 duplicatas completas, 0 ausentes, 0
inconsistencias logicas).

## Rastreabilidade

A transformacao silver -> gold (criacao dos indicadores e variaveis
derivadas) esta documentada em `notebooks/2_transformation.ipynb` e
resulta em `data/gold/food_wastage_gold.csv`.

# Camada bronze

Camada de dados **crus**, como recebidos da fonte original, sem
transformacoes alem da ingestao.

## Arquivo

- `food_wastage_bronze.csv` - copia exata do arquivo original, **1782
  linhas x 11 colunas**, sem renomeacao de colunas, conversao de tipos ou
  remocao de registros.

## Fonte

Dataset **Food Wastage Data in Restaurant**, obtido no Kaggle:
<https://www.kaggle.com/datasets/trevinhannibal/food-wastage-data-in-restaurant>

Segundo a descricao do Kaggle, reune dados de desperdicio de alimentos de
um restaurante, organizados para pesquisa sobre padroes e magnitude do
desperdicio.

## Unidade de analise

Cada linha representa **um registro/evento de desperdicio de alimentos**
(um preparo/servico associado a um evento).

## Limitacoes conhecidas da fonte (herdadas em todas as camadas seguintes)

- Nao ha identificador unico por evento (sem chave primaria).
- A unidade das colunas `Quantity of Food` e `Wastage Food Amount` nao e
  declarada pela fonte (assume-se quilogramas nas camadas seguintes, mas
  isso e uma inferencia, nao uma confirmacao).
- Nao ha variavel temporal (data do evento), o que impede analisar
  tendencia historica, sazonalidade real ou efeito de feriados.
- Nao ha garantia documentada de representatividade estatistica (nao se
  pode afirmar que os padroes observados se generalizam para outros
  restaurantes, buffets ou regioes).

## Rastreabilidade

A transformacao bronze -> silver esta documentada em
`notebooks/1_cleaning.ipynb`.

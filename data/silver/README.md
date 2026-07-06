# Camada silver

Camada de dados **limpos e padronizados**: tipos corrigidos, valores
tratados e colunas normalizadas a partir da camada bronze, ainda sem os
indicadores finais de negocio.

Esta pasta faz parte da estrutura do pipeline (bronze -> silver -> gold) e e
versionada mesmo sem arquivos de dados, para documentar a rastreabilidade das
camadas. Neste projeto, a base ja tratada e disponibilizada diretamente na
camada gold (`data/gold/food_wastage_gold.csv`), que e o insumo usado pelo
dashboard e pela analise.

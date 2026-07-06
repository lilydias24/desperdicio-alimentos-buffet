# Camada bronze

Camada de dados **crus**, como recebidos da fonte original (Kaggle), sem
transformacoes alem da ingestao.

Esta pasta faz parte da estrutura do pipeline (bronze -> silver -> gold) e e
versionada mesmo sem arquivos de dados, para documentar a rastreabilidade das
camadas. Neste projeto, a base ja tratada e disponibilizada diretamente na
camada gold (`data/gold/food_wastage_gold.csv`), que e o insumo usado pelo
dashboard e pela analise.

# Investigacao do Desperdicio de Alimentos em Servicos de Buffet

Entrega final da disciplina de Introducao a Ciencia de Dados - Grupo 03.

**Integrantes:** Arthur Provenzi Parizotto, Bianca Maia Ribeiro, Emilly
Nascimento Dias e Rafael Jaques do Nascimento Lopes.

![Dashboard: indicadores gerais de desperdício com filtros por método de preparo, preço, tipo de evento e alimento](docs/img/dashboard-indicadores.png)

![Dashboard: distribuição da taxa de desperdício por tipo de alimento (Q1)](docs/img/dashboard-analises.png)

## Problema

Servicos de buffet precisam estimar, com antecedencia, quanto alimento
preparar para cada evento. Errar essa estimativa gera desperdicio de comida,
custo operacional e impacto ambiental. O projeto investiga **em que condicoes
o desperdicio tende a ser maior**, para apoiar decisoes de planejamento de
producao em eventos.

## Perguntas analiticas

- **Q1** - O metodo de preparo e as condicoes de armazenamento influenciam o
  volume de desperdicio, considerando o tipo de alimento?
- **Q2** - Como o tipo e o porte do evento se relacionam com o desperdicio?
- **Q3** - Qual a relacao entre quantidade produzida, faixa de preco
  (pricing) e taxa de desperdicio?
- **Q4** - Quais perfis operacionais concentram maior risco de desperdicio?

## Fontes dos dados

A base original (**Food Wastage Data in Restaurant**) foi obtida no
[Kaggle](https://www.kaggle.com/datasets/trevinhannibal/food-wastage-data-in-restaurant)
e ingerida na camada bronze do pipeline (`data/bronze/food_wastage_bronze.csv`,
1782 registros). Apos limpeza (remocao de 164 duplicatas completas) e
padronizacao, a base silver (`data/silver/food_wastage_silver.csv`, 1618
registros) alimenta a criacao dos indicadores, resultando na camada gold
(`data/gold/food_wastage_gold.csv`), com 1618 eventos e 21 colunas, que e o
unico insumo usado pelo dashboard e pela analise. Cada linha representa um
registro/evento de desperdicio de alimentos (unidade de analise constante
em todas as camadas). Ver `data/bronze/README.md` e `data/silver/README.md`
para a rastreabilidade completa, e `notebooks/` para os notebooks originais
de limpeza, transformacao e AED.

## Resumo das etapas anteriores

1. **Definicao do problema e AED** - exploracao inicial da base, formulacao
   das perguntas Q1-Q4 e das hipoteses exploratorias HE-01 a HE-06.
2. **Preparacao dos dados (Parte 3)** - organizacao das camadas
   bronze/silver/gold, criacao dos indicadores (`wastage_rate`,
   `wastage_per_guest`, `event_profile`, `waste_risk_rank`, etc.) e validacao
   automatizada da camada gold.
3. **Analise estatistica (Parte 1)** - validacao formal das hipoteses com
   testes estatisticos.
4. **Dashboard (Parte 2)** - aplicacao Streamlit que comunica o pipeline
   completo.
5. **Reprodutibilidade e documentacao (Parte 4)** - Docker, compose e este
   README.

## Ajustes realizados a partir dos feedbacks

Pareceres formativos e somativos foram recebidos em cada entrega parcial e
final. Principais ajustes incorporados:

- **Contexto e objetivo (Entrega 1):** reduzidas redundancias do texto,
  removida a antecipacao de solucao, e delimitado melhor o escopo
  (unidade de analise, fonte, publico-alvo). Nota final: 9/10. Ponto ainda
  em aberto e explicitamente reconhecido: o objetivo ainda cobre multiplos
  fatores simultaneamente e algumas variaveis derivadas (`event_size`,
  `event_profile`) tinham definicao operacional pouco explicita - por
  isso, a definicao exata de cada faixa (quartis/tercis) e cada perfil
  esta agora documentada em `docs/dicionario_indicadores.md` e nos
  notebooks de preparacao.
- **Especificacao do dataset (Entrega 2):** adicionada a URL completa do
  dataset no Kaggle (antes citado sem link direto), e documentada a
  unidade inferida (nao confirmada pela fonte) de `quantity_of_food` e
  `wastage_food_amount`, alem do reconhecimento explicito de que
  `purchase_history` e `seasonality` tem significado ambiguo na fonte -
  por isso essas colunas nao sao usadas como filtros ou variaveis de
  analise no dashboard. Nota final: 9/10.
- **Preparacao dos dados / pipeline (Entrega 3):** o parecer elogiou a
  camada gold orientada as perguntas do projeto, mas apontou que os
  criterios de remocao de registros (1782 -> 1618) estavam pouco
  discutidos e que a unidade de analise da gold precisava ser declarada
  explicitamente. Em resposta, `data/bronze/README.md` e
  `data/silver/README.md` agora documentam o criterio exato (164
  duplicatas completas removidas, 0 por ausencia ou inconsistencia
  logica) e a unidade de analise (um evento por linha) e reafirmada em
  `docs/dicionario_indicadores.md` e na pagina "Contexto e problema" do
  dashboard. O parecer tambem alertou que as colunas `mean_wastage_*`
  podem gerar vazamento de informacao em modelagem preditiva futura; essa
  ressalva foi documentada no dicionario de indicadores. Nota final: 9,0.
- **Analise Exploratoria de Dados (AED):** o parecer somativo (nota 9,5)
  identificou dois pontos fracos: (1) o nome do notebook nao seguia o
  padrao pedido (`grad_grupo_3_aed.ipynb` em vez de
  `grad_grupo_03_aed.ipynb`) - corrigido ao versionar o notebook em
  `notebooks/grad_grupo_03_aed.ipynb`; (2) alguns rotulos usavam
  linguagem mais forte que a evidencia descritiva sustentava (ex.:
  "pricing como fator dominante", "efeito do armazenamento", "pricing e
  metodo de preparo atuam de forma aditiva"), sugerindo estrutura
  explicativa nao estimada formalmente. Essa cautela terminologica foi
  aplicada de forma consistente no dashboard (Parte 2): os textos de
  leitura evitam a palavra "efeito" fora do sentido estatistico formal
  ("tamanho de efeito") e a pagina de conclusoes caracteriza o perfil
  `Pequeno | Sit-down Dinner | High` como "perfil de maior taxa
  observada", sem atribuir uma forma funcional (aditividade) nao
  demonstrada.

## Etapa de analise (Parte 1)

Script que valida as hipoteses exploratorias (HE-01 a HE-06) com testes
estatisticos formais: teste t de Welch, Kruskal-Wallis, bootstrap de
intervalo de confianca e correlacao de Pearson/Spearman. Cada analise
reporta estimativa, IC 95%, valor-p e tamanho de efeito, evitando
conclusoes causais (dados observacionais).

```bash
python analysis/analise_estatistica.py
```

Le `data/gold/food_wastage_gold.csv` e gera em `outputs/analise/`:

- `resumo_analises.csv` - estimativa, IC 95%, p-valor e tamanho de efeito por analise.
- `estatisticas_grupos.csv` - estatisticas descritivas por grupo.
- `perfis_risco.csv` - ranking de perfis operacionais por taxa media de desperdicio.
- `relatorio_analise.md` - relatorio consolidado em markdown.

Principais achados: Sit-down Dinner desperdica mais que os demais metodos de
preparo (7,51% vs. 6,06-7,02%, p < 0,001); pricing High e a variavel isolada
mais associada ao desperdicio (8,81% vs. 5,46-5,84%, p < 0,001); a diferenca
de desperdicio por armazenamento, observada de forma descritiva na AED para
Baked Goods e Dairy Products, **nao se confirma no teste formal por
alimento** (p = 0,076 e p = 0,058, ambos acima de 0,05) - HE-02 e
classificada como rejeitada na etapa de analise; e o perfil de maior taxa
observada e `Pequeno | Sit-down Dinner | High` (~11,1%, com ressalva de
amostra pequena).

## Indicadores

Definicoes completas em `docs/dicionario_indicadores.md`. Principais formulas:

- `wastage_rate = wastage_food_amount / quantity_of_food * 100` (taxa de desperdicio, em %)
- `wastage_per_guest = wastage_food_amount / number_of_guests` (desperdicio por convidado)
- `event_profile = event_size | preparation_method | pricing` (perfil operacional)
- `waste_risk_rank`: ranking do `event_profile` pela taxa media de
  desperdicio, em ordem decrescente (1 = maior risco).

A validacao automatizada da camada gold (colunas obrigatorias, ausentes,
duplicatas, consistencia logica e formulas dos indicadores) esta em:

```bash
python analysis/validacao_camada_gold.py   # exit code 0 = camada valida
```

Resultado detalhado em `docs/checklist_validacao_gold.md`.

## Estrutura do dashboard (Parte 2)

Aplicacao Streamlit com cinco paginas:

- **Contexto e problema** - problema, publico-alvo, fonte dos dados,
  escopo/unidade de analise, perguntas Q1-Q4 e amostra da base gold.
- **Indicadores gerais** - taxa media de desperdicio, desperdicio medio por
  evento, desperdicio por convidado, quantidade media produzida, perfil de
  maior risco e maior diferenca entre grupos, para a selecao atual de filtros.
- **Analises por pergunta** - uma aba por pergunta (Q1 a Q4), cada uma com o
  grafico mais adequado (boxplot/violin, barras, heatmap, scatter ou ranking)
  e um texto curto de interpretacao.
- **Perfis de risco** - ranking completo dos perfis operacionais por taxa
  media de desperdicio, com tabela detalhada.
- **Conclusoes e limitacoes** - situacao de cada hipotese (confirmada,
  rejeitada ou nao avaliavel), com ressalvas quando aplicavel, e cuidados
  de interpretacao.

Filtros na barra lateral (validos para todas as paginas, exceto "Contexto e
problema"): metodo de preparo, pricing, tipo de evento, tipo de alimento,
porte do evento e condicao de armazenamento. Todos iniciam com todas as
opcoes selecionadas e o botao "Limpar filtros" restaura a selecao completa.

### Personalizacao visual e elementos interativos

- **Tema** (`.streamlit/config.toml`) e paleta de graficos
  (`app/utils/palette.py`) usam a mesma familia de verdes; CSS customizado
  (`app/utils/styling.py`) estiliza cartoes de indicador, cabecalhos,
  sidebar e botoes.
- **Modais** (`app/components/modals.py`, via `st.dialog`): "Glossario" e
  "Como ler" na barra lateral, e "Ver detalhes" de um perfil especifico na
  pagina *Perfis de risco* (com badge de nivel de risco).
- **Controles interativos**: alternancia boxplot/violin no grafico de
  metodo de preparo (*Indicadores gerais*) e slider de quantos perfis
  mostrar no ranking (*Perfis de risco*).

## Estrutura do repositorio

```text
.
├── app/                          # dashboard Streamlit (Parte 2)
│   ├── app.py                    # ponto de entrada
│   ├── components/               # filtros, indicadores, graficos e modais
│   ├── services/                 # carregamento e filtragem da base gold
│   └── utils/                    # formatacao, paleta de cores e CSS customizado
├── analysis/                     # etapa de analise (Parte 1) e validacao (Parte 3)
│   ├── analise_estatistica.py
│   └── validacao_camada_gold.py
├── notebooks/                    # notebooks originais das entregas parciais
│   ├── 1_cleaning.ipynb          # bronze -> silver
│   ├── 2_transformation.ipynb    # silver -> gold
│   └── grad_grupo_03_aed.ipynb   # analise exploratoria de dados (AED)
├── data/
│   ├── bronze/food_wastage_bronze.csv  # dado cru (1782 linhas)
│   ├── silver/food_wastage_silver.csv  # dado limpo/padronizado (1618 linhas)
│   └── gold/food_wastage_gold.csv      # base final usada pelo app e pela analise
├── docs/
│   ├── dicionario_indicadores.md
│   └── checklist_validacao_gold.md
├── outputs/                      # saidas geradas pelos scripts (nao versionadas)
├── Dockerfile                    # imagem do dashboard (Parte 4)
├── compose.yaml                  # orquestracao com Docker Compose (Parte 4)
├── requirements.txt              # dependencias Python
├── apresentar.ps1 / apresentar.sh  # sobe o dashboard com um comando (demo/apresentacao)
├── parar.ps1 / parar.sh            # encerra o dashboard
├── README.md
└── DIVISAO_RESPONSABILIDADES.md
```

Todos os caminhos de dados sao relativos (resolvidos a partir da raiz do
repositorio), compativeis com execucao local e via Docker.

## Instrucoes de execucao

### Script rapido (recomendado para demo/apresentacao)

Na raiz do repositorio, execute:

```powershell
powershell -ExecutionPolicy Bypass -File apresentar.ps1   # Windows
```

```bash
./apresentar.sh                                            # Linux/Mac/Git Bash
```

O script detecta Docker automaticamente e roda `docker compose up --build
-d`; se o Docker nao estiver disponivel na maquina, cai para execucao
local com Python. Em ambos os casos, espera o dashboard responder e abre
o navegador em `http://localhost:8501` sozinho. Para encerrar, use
`parar.ps1` (Windows) ou `./parar.sh` (Linux/Mac/Git Bash).

### Com Docker (recomendado)

Requisito: Docker com o plugin Compose. Na raiz do repositorio:

```bash
docker compose up --build
```

### Sem Docker (execucao local)

Requisito: Python 3.10 ou superior.

```bash
pip install -r requirements.txt
streamlit run app/app.py
```

## Endereco de acesso

Apos iniciar (por Docker ou localmente), o dashboard fica disponivel em:

**<http://localhost:8501>**

## Procedimento para encerramento

- **Docker (em primeiro plano):** `Ctrl+C` no terminal e, em seguida,
  `docker compose down` para remover o container.
- **Execucao local:** `Ctrl+C` no terminal onde o Streamlit esta rodando.

## Limitacoes conhecidas

- Os dados sao **observacionais**: as associacoes encontradas (ex.: pricing
  High com maior desperdicio) nao permitem conclusoes causais.
- Alguns perfis operacionais tem **poucos eventos** (o perfil de maior risco
  tem 18 ocorrencias), tornando suas medias instaveis; esses perfis sao
  sinalizados como de baixa confianca no dashboard.
- A base cobre um unico conjunto de eventos obtido no Kaggle, sem
  informacao de periodo, regiao ou custo monetario do desperdicio, o que
  limita a generalizacao dos resultados.
- A correlacao entre quantidade produzida e taxa de desperdicio e fraca a
  moderada (r = 0,25); quantidade, isolada, nao e bom preditor.
- A unidade de `quantity_of_food` e `wastage_food_amount` (assumida como
  quilogramas) e uma inferencia do grupo: a fonte original nao a declara.
- Os atributos `purchase_history`, `seasonality` e `geographical_location`
  tem significado operacional ambiguo na fonte e por isso nao sao usados
  como filtros ou variaveis de analise no dashboard.
- As colunas `mean_wastage_by_prep_method`, `mean_wastage_rate_by_food_type`
  e `mean_wastage_rate_by_profile` foram calculadas sobre toda a base; nao
  devem ser usadas como features em modelagem preditiva futura sem
  recalculo restrito ao conjunto de treino (risco de vazamento de dados).
- O dataset nao possui identificador unico por evento; a remocao de
  duplicatas completas (164 registros, ver `data/silver/README.md`) e
  tecnicamente justificavel mas nao elimina a possibilidade de dois
  eventos reais terem sido registrados com os mesmos valores.

## Declaracao de uso de Inteligencia Artificial

O grupo utilizou a ferramenta **Claude Code (Anthropic)** como assistente de
programacao durante o desenvolvimento: apoio na escrita de codigo do
dashboard e dos scripts de analise, na configuracao de reprodutibilidade
(Dockerfile, compose.yaml) e na redacao de documentacao. Todo o conteudo
gerado com apoio de IA foi revisado, testado e validado pelos integrantes,
que sao responsaveis pelas decisoes analiticas, pela interpretacao dos
resultados e pelo conteudo final entregue.

## Divisao de responsabilidades

Detalhamento completo em `DIVISAO_RESPONSABILIDADES.md`.

| Parte | Frente principal | Peso |
| --- | --- | --- |
| Parte 1 | Analise estatistica e validacao das hipoteses | 25% |
| Parte 2 | Dashboard Streamlit e experiencia interativa | 25% |
| Parte 3 | Dados, indicadores e rastreabilidade do pipeline | 25% |
| Parte 4 | Reprodutibilidade, Docker e documentacao final | 25% |

## Minha contribuição

- Desenvolvimento do dashboard interativo em Streamlit: componentes, serviços e
  utilitários da aplicação, além dos ajustes finais de interface.
- Scripts de inicialização rápida para a apresentação.
- Preparação da base gold para execução local, `requirements.txt` e atualização do
  README com a estrutura do dashboard e da análise.

> Este repositório é uma cópia, com histórico, do original do grupo no GitLab da
> UNIPAMPA (privado). Os e-mails dos colaboradores foram anonimizados no histórico.

## Repositorio e submissao

```bash
git clone https://gitlab.unipampa.edu.br/ales/icd-2026.1/grupo-03.git
```

A versao submetida corresponde a tag `entrega-final`:

```bash
git checkout entrega-final
```

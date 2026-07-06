# Investigacao do Desperdicio de Alimentos em Servicos de Buffet

Entrega final da disciplina de Introducao a Ciencia de Dados - Grupo 03.

**Integrantes:** Arthur Provenzi Parizotto, Bianca Maia Ribeiro, Emilly
Nascimento Dias e Rafael Jacques do Nascimento Lopes.

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

A base original (**Food Wastage Data**) foi obtida no
[Kaggle](https://www.kaggle.com/) e ingerida na camada bronze do pipeline.
Apos limpeza, padronizacao e criacao de indicadores, a base final e
disponibilizada na camada gold (`data/gold/food_wastage_gold.csv`), com 1618
eventos e 21 colunas, que e o unico insumo usado pelo dashboard e pela
analise. Ver `data/bronze/README.md` e `data/silver/README.md` para a
rastreabilidade das camadas.

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
preparo (7,51% vs. 6,06-7,02%); pricing High e a variavel isolada mais
associada ao desperdicio (8,81% vs. 5,46-5,84%); o efeito do armazenamento e
condicional ao tipo de alimento; e o perfil de maior risco e
`Pequeno | Sit-down Dinner | High` (~11,1%, com ressalva de amostra pequena).

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

- **Contexto e problema** - problema, perguntas Q1-Q4 e amostra da base gold.
- **Indicadores gerais** - taxa media de desperdicio, desperdicio medio por
  evento, desperdicio por convidado, quantidade media produzida, perfil de
  maior risco e maior diferenca entre grupos, para a selecao atual de filtros.
- **Analises por pergunta** - uma aba por pergunta (Q1 a Q4), cada uma com o
  grafico mais adequado (boxplot/violin, barras, heatmap, scatter ou ranking)
  e um texto curto de interpretacao.
- **Perfis de risco** - ranking completo dos perfis operacionais por taxa
  media de desperdicio, com tabela detalhada.
- **Conclusoes e limitacoes** - situacao de cada hipotese (confirmada,
  rejeitada ou parcialmente confirmada) e cuidados de interpretacao.

Filtros na barra lateral (validos para todas as paginas, exceto "Contexto e
problema"): metodo de preparo, pricing, tipo de evento, tipo de alimento,
porte do evento e condicao de armazenamento. Todos iniciam com todas as
opcoes selecionadas e o botao "Limpar filtros" restaura a selecao completa.

## Estrutura do repositorio

```text
.
├── app/                          # dashboard Streamlit (Parte 2)
│   ├── app.py                    # ponto de entrada
│   ├── components/               # filtros, indicadores e graficos
│   ├── services/                 # carregamento e filtragem da base gold
│   └── utils/                    # formatacao de numeros e percentuais
├── analysis/                     # etapa de analise (Parte 1) e validacao (Parte 3)
│   ├── analise_estatistica.py
│   └── validacao_camada_gold.py
├── data/
│   ├── bronze/                   # dados crus (documentacao da camada)
│   ├── silver/                   # dados limpos (documentacao da camada)
│   └── gold/food_wastage_gold.csv# base final usada pelo app e pela analise
├── docs/
│   ├── dicionario_indicadores.md
│   └── checklist_validacao_gold.md
├── outputs/                      # saidas geradas pelos scripts (nao versionadas)
├── Dockerfile                    # imagem do dashboard (Parte 4)
├── compose.yaml                  # orquestracao com Docker Compose (Parte 4)
├── requirements.txt              # dependencias Python
├── README.md
└── DIVISAO_RESPONSABILIDADES.md
```

Todos os caminhos de dados sao relativos (resolvidos a partir da raiz do
repositorio), compativeis com execucao local e via Docker.

## Instrucoes de execucao

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

## Repositorio e submissao

```bash
git clone https://gitlab.unipampa.edu.br/ales/icd-2026.1/grupo-03.git
```

A versao submetida corresponde a tag `entrega-final`:

```bash
git checkout entrega-final
```

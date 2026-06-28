# Divisao de Responsabilidades - Entrega Final

Projeto: Investigacao do Desperdicio de Alimentos em Servicos de Buffet  
Grupo 03: Arthur Provenzi Parizotto, Bianca Maia Ribeiro, Emilly Nascimento Dias e Rafael Jacques do Nascimento Lopes

Este documento organiza a divisao do trabalho da entrega final de forma equilibrada entre os quatro integrantes. A divisao foi baseada no enunciado da atividade, nos notebooks de apoio sobre analise estatistica e na Analise Exploratoria de Dados ja produzida pelo grupo.

O objetivo comum e entregar um dashboard em Streamlit que consolide o pipeline completo: problema, dados, preparacao, exploracao, analise e comunicacao. Cada pessoa fica responsavel por uma frente principal, mas todas devem revisar pelo menos uma parte feita por outro integrante para garantir coerencia tecnica e rastreabilidade.

## Entregaveis obrigatorios considerados

- Aplicacao Streamlit funcional.
- Uso preferencial da camada gold (`food_wastage_gold.csv`).
- Analises finais baseadas nas perguntas Q1, Q2, Q3 e Q4.
- Indicadores documentados e coerentes com o problema.
- Visualizacoes com titulos, eixos, unidades, legendas e interpretacoes.
- Interatividade por filtros relevantes.
- Secao de conclusoes, limitacoes e cuidados de interpretacao.
- `Dockerfile`, `compose.yaml` e `requirements.txt`.
- `README.md` completo.
- Declaracao de uso de Inteligencia Artificial.
- Tag final `entrega-final`.

## Divisao igualitaria

| Integrante | Frente principal | Entregas individuais | Peso aproximado |
|---|---|---|---|
| Parte 1 | Analise estatistica e validacao das hipoteses | Script de analise final, testes estatisticos, intervalos de confianca, tamanhos de efeito e interpretacao tecnica | 25% |
| Parte 2 | Dashboard Streamlit e experiencia interativa | Estrutura da aplicacao, paginas/secoes, filtros, indicadores visuais, graficos interativos e textos curtos no dashboard | 25% |
| Parte 3 | Dados, indicadores e rastreabilidade do pipeline | Organizacao das camadas de dados, validacao da camada gold, calculo/documentacao dos indicadores e conferencia dos resultados com a AED | 25% |
| Parte 4 | Reprodutibilidade, Docker e documentacao final | `Dockerfile`, `compose.yaml`, `requirements.txt`, README final, instrucoes de execucao, encerramento e submissao/tag | 25% |

## Parte 1 - Analise estatistica e validacao das hipoteses

Responsabilidade principal: transformar as hipoteses exploratorias da AED em analises finais mais estruturadas, seguindo o modelo dos notebooks do professor.

Tarefas:

- Selecionar quais hipoteses serao avaliadas na entrega final.
- Relacionar cada analise com as perguntas do projeto:
  - Q1: metodo de preparo, armazenamento e tipo de alimento.
  - Q2: tipo e porte do evento.
  - Q3: quantidade produzida, pricing e taxa de desperdicio.
  - Q4: perfis operacionais de maior risco.
- Calcular estatisticas descritivas finais por grupo.
- Aplicar procedimentos estatisticos adequados, quando fizer sentido:
  - teste t de Welch ou Mann-Whitney para comparacoes entre dois grupos;
  - ANOVA ou Kruskal-Wallis para comparacoes com tres ou mais grupos;
  - qui-quadrado para associacoes entre variaveis categoricas;
  - Pearson ou Spearman para associacoes numericas;
  - bootstrap ou intervalo de confianca para medias/diferencas relevantes.
- Reportar estimativa, intervalo de confianca, valor-p, tamanho de efeito e limitacoes.
- Evitar conclusoes causais, pois o dataset e observacional.

Entregas esperadas:

- `analysis/analise_estatistica.py` com a etapa de analise.
- Tabela-resumo das analises finais para alimentar o dashboard e o README.
- Texto curto com conclusoes tecnicas e cuidados de interpretacao.

Revisao cruzada:

- Revisar se os graficos e indicadores do dashboard representam corretamente os resultados estatisticos.

## Parte 2 - Dashboard Streamlit e experiencia interativa

Responsabilidade principal: construir a aplicacao Streamlit como camada de comunicacao do projeto, evitando que ela seja apenas uma colecao solta de graficos.

Tarefas:

- Criar a estrutura da aplicacao em `app/`.
- Definir a navegacao do dashboard, por exemplo:
  - Contexto e problema.
  - Indicadores gerais.
  - Analises por pergunta.
  - Perfis de risco.
  - Conclusoes e limitacoes.
- Implementar filtros relevantes:
  - metodo de preparo;
  - pricing;
  - tipo de evento;
  - tipo de alimento;
  - porte do evento;
  - condicao de armazenamento.
- Criar indicadores principais:
  - taxa media de desperdicio;
  - desperdicio medio por evento;
  - desperdicio por convidado;
  - quantidade media produzida;
  - perfil de maior risco;
  - diferenca entre grupos relevantes.
- Desenvolver visualizacoes adequadas:
  - boxplots ou violin plots para distribuicoes;
  - barras para comparacoes de medias;
  - heatmaps para interacoes como `pricing x preparation_method`;
  - ranking dos perfis de maior risco;
  - scatter plot para `quantity_of_food x wastage_rate`.
- Inserir textos curtos de interpretacao junto aos graficos.
- Garantir que a aplicacao inicie com filtros validos e sem erros.

Entregas esperadas:

- `app/app.py` funcional.
- Componentes ou funcoes auxiliares em `app/components/`, `app/services/` ou `app/utils/`, se necessario.
- Dashboard executando localmente em `http://localhost:8501`.

Revisao cruzada:

- Revisar se o README explica corretamente a estrutura do dashboard e seus controles.

## Parte 3 - Dados, indicadores e rastreabilidade do pipeline

Responsabilidade principal: garantir que os dados usados no dashboard sejam os mesmos do projeto, estejam organizados corretamente e sustentem os indicadores.

Tarefas:

- Organizar a estrutura de dados esperada:
  - `data/bronze/`;
  - `data/silver/`;
  - `data/gold/`.
- Garantir que a camada gold esteja disponivel no repositorio ou que exista mecanismo claro para obte-la.
- Conferir se `food_wastage_gold.csv` contem as variaveis necessarias:
  - `type_of_food`;
  - `event_type`;
  - `number_of_guests`;
  - `quantity_of_food`;
  - `wastage_food_amount`;
  - `preparation_method`;
  - `storage_conditions`;
  - `pricing`;
  - `wastage_rate`;
  - `wastage_per_guest`;
  - `event_size`;
  - `quantity_tier`;
  - `event_profile`;
  - `waste_risk_rank`.
- Conferir valores ausentes, duplicatas e consistencia logica.
- Validar os calculos dos indicadores:
  - `wastage_rate = wastage_food_amount / quantity_of_food * 100`;
  - `wastage_per_guest = wastage_food_amount / number_of_guests`;
  - rankings e medias por perfil.
- Comparar os principais numeros do dashboard com os resultados da AED.
- Documentar ajustes feitos nos dados ou indicadores.

Entregas esperadas:

- Dados organizados em caminhos relativos.
- Dicionario simples de indicadores para o README.
- Checklist de validacao da camada gold.

Revisao cruzada:

- Revisar o script de analise para confirmar que os dados e variaveis usados estao corretos.

## Parte 4 - Reprodutibilidade, Docker e documentacao final

Responsabilidade principal: garantir que o projeto possa ser executado por outra pessoa com um unico comando e que o repositorio esteja pronto para avaliacao.

Tarefas:

- Criar ou revisar `requirements.txt` com as bibliotecas necessarias, por exemplo:
  - `streamlit`;
  - `pandas`;
  - `numpy`;
  - `plotly`;
  - `scipy`;
  - `matplotlib` ou `seaborn`, se forem usados.
- Criar `Dockerfile` com:
  - imagem Python adequada;
  - instalacao das dependencias;
  - copia dos arquivos do projeto;
  - exposicao da porta `8501`;
  - comando de inicializacao do Streamlit.
- Criar `compose.yaml` para executar:

```bash
docker compose up --build
```

- Testar a execucao em ambiente limpo.
- Atualizar o `README.md` com:
  - nome do projeto;
  - integrantes;
  - problema;
  - perguntas analiticas;
  - fontes dos dados;
  - resumo das etapas anteriores;
  - etapa de analise;
  - indicadores;
  - estrutura do dashboard;
  - estrutura do repositorio;
  - instrucoes de execucao;
  - endereco de acesso;
  - procedimento para encerramento;
  - limitacoes conhecidas;
  - declaracao de uso de IA;
  - divisao de responsabilidades.
- Preparar a submissao:
  - conferir `git status`;
  - criar a tag `entrega-final`;
  - obter o hash do commit associado.

Entregas esperadas:

- `Dockerfile`.
- `compose.yaml`.
- `requirements.txt`.
- `README.md` completo e revisado.
- Instrucoes de submissao prontas.

Revisao cruzada:

- Revisar se o dashboard roda corretamente com os dados reais e se todos os arquivos necessarios estao versionados.

## Responsabilidades compartilhadas

Estas tarefas devem ser feitas em conjunto ou revisadas por todos:

- Confirmar que o problema analitico nao mudou em relacao as entregas parciais.
- Garantir que o dashboard responda claramente as perguntas Q1, Q2, Q3 e Q4.
- Validar que cada grafico tem uma finalidade analitica.
- Conferir se as interpretacoes sao sustentadas pelos dados.
- Evitar afirmacoes causais nao justificadas.
- Revisar ortografia, titulos, rotulos, unidades e legendas.
- Testar a aplicacao antes da entrega final.
- Garantir que nenhum caminho absoluto do computador de um integrante seja necessario.
- Conferir se a tag `entrega-final` foi criada somente depois da validacao final.




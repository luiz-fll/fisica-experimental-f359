# Registro de alterações

Este arquivo é cumulativo e append-only. Cada execução de trabalho acrescenta uma entrada curta ao final. Não reescrever nem apagar entradas anteriores. Não é necessário ler o histórico inteiro para acrescentar uma nova entrada.

## 2026-11-08 — Preparação do fluxo agêntico

### Alterações
- Criados os documentos de instruções, contexto científico, especificação do software, tarefas, estado atual e handoff.
- Registrada a proteção explícita da pasta `parcial/`.
- Formalizados os formatos de entrada, métodos de análise, saídas esperadas e arquitetura modular.

### Verificações
- Documentação inicial preparada com base no relatório parcial fornecido e nas decisões de arquitetura discutidas.

### Pendências
- Implementar o pipeline final.
- Completar os CSVs de entrada das filmagens reais.
- Criar e executar a suíte de testes.

## 2026-11-20 — Revisão documental do estado atual

### Alterações
- Alinhados README, instruções de agentes, especificação, estado atual, tarefas e handoff à estrutura real do pacote.
- Registrada a localização da implementação em `final/`, os seis módulos vazios e o papel limitado de `final/teste.py`.
- Atualizados os contratos documentais para os cabeçalhos CSV observados (`tempo_seg`, `temperatura_c`) e para a estrutura atual dos nove conjuntos de dados.
- Reforçada a proteção de `parcial/` e dos diretórios de dados brutos.

### Verificações
- Inventariados os arquivos Markdown fora de `parcial/`.
- Inspecionados os nomes, tamanhos e conteúdo dos módulos Python em `final/`.
- Conferidos cabeçalhos e contagens de linhas dos quatro CSVs nas nove filmagens reais e no conjunto de exemplo.
- Nenhum dado, script ou arquivo não-Markdown foi alterado.

### Pendências
- Implementação do pipeline e testes automatizados continuam pendentes.

## 2026-11-20 — Fundação do projeto (Prioridade 0)

### Alterações
- Criados `requirements.txt` (numpy, pandas, matplotlib; Python 3.10+ declarado), `requirements-dev.txt` (acrescenta pytest) e `pytest.ini` (`testpaths=tests`, `pythonpath=final`).
- `final/periodos.py`: implementadas `definir_limites_janelas` e `atribuir_janela` com a convenção `[início, fim)`, último limite fechado, `N = max(1, ceil(t_fim/L))`, origem 0 s; constantes de mínimos para períodos.
- `final/massa.py`: constantes de mínimos (3 leituras para ajuste; 5 recomendadas).
- Contratos (assinaturas, docstrings, `NotImplementedError`) em `analisar.py`, `pipeline.py`, `massa.py`, `graficos.py`, `relatorio.py` e demais funções de `periodos.py`. `analisar.py` ganhou `ErroFilmagem` e uma CLI que retorna código 2 com aviso.
- Criada a pasta `tests/` com 29 testes (janelas, políticas, importação dos módulos). Teste de mutação confirmou que alterações nas fronteiras são detectadas.
- Atualizados `PROJECT.md` (6.3, 6.4, 9), `TASKS.md`, `CURRENT_STATE.md`, `HANDOFF.md`, `README.md` e `final/README.md`.

### Verificações
- `python -m pytest`: 29 passed.
- Convenção de janelas aplicada aos nove conjuntos reais em modo leitura: nenhuma observação sem janela; a última janela contém uma leitura de massa em 8 de 9 filmagens (pendência registrada).
- Dados, `dados_old/`, `dados_exemplo/`, `parcial/` e `resultados/` comparados com o pacote recebido: idênticos.

### Pendências
- Decisão metodológica sobre a última janela (ver `PROJECT.md` 6.3).
- Implementação de todas as funções de cálculo, CLI, pipeline, gráficos e relatórios.
- Verificação dos limites inferiores de versão e de Python 3.10/3.11.

## 2026-11-20 — Ajustes da fundação: última janela e imports

### Alterações
- `final/periodos.py`: a última janela passa a absorver o resto do ensaio, `[(N-1)·L, t_fim]`, com `N = max(1, floor(t_fim/L))` (decisão do pesquisador). Substitui a convenção `ceil`, que gerava janelas com uma única leitura.
- Imports padronizados como `from final.<modulo> import ...`; `final/__init__.py` criado (pacote regular); `pytest.ini` com `pythonpath = .`.
- Testes atualizados (35 passando): absorção da última janela, tolerância numérica, duração personalizada e caso real de 600,007 s.
- `PROJECT.md` (6.3, 8, 9), `TASKS.md`, `CURRENT_STATE.md`, `HANDOFF.md` e READMEs atualizados; pendência da última janela encerrada.

### Verificações
- `python -m pytest`: 35 passed.
- Mutação (última janela sem absorção): 5 testes falham.
- `python -m final.analisar`: retorna código 2 com aviso (CLI não implementada).
- Nove conjuntos reais: 3 janelas por filmagem, com 9, 10 e 11 leituras de massa; nenhuma observação sem janela.
- Dados e `parcial/` não alterados.

### Pendências
- Implementação das funções de cálculo, CLI, pipeline, gráficos e relatórios.

## 2026-11-20 — Prioridade 1: entrada e validação

### Alterações
- `final/analisar.py`: CLI com `--diretorio`, `--saida` e `--janela`; `descobrir_filmagens` (subpastas diretas, sem ocultas, ordenadas); `carregar_filmagem` lê cada CSV uma vez, valida cabeçalhos exatos, campos, valores numéricos e finitos, ordem e duplicatas de tempos, mínimos por arquivo, condições e relações entre arquivos; `validar_lote` isola falhas por filmagem; `Problema` e `ErroFilmagem` reportam arquivo e linha. A CLI não grava resultados.
- Avisos (não bloqueantes): espaços ao redor de valores, mergulhos fora do intervalo do tracker ou da massa, ângulos de mergulho divergentes do tracker acima de 2°.
- `tests/test_analisar.py` (49 casos, sintéticos, incluindo parametrizações) e `tests/test_dados_reais.py` (somente leitura). Total: 85 testes.
- Atualizados `PROJECT.md` (5, 8, 9), `TASKS.md`, `CURRENT_STATE.md`, `HANDOFF.md` e READMEs.

### Verificações
- `python -m pytest`: 85 passed.
- Mutação: remover checagem de duplicatas e remover isolamento do lote fazem testes falharem.
- `python -m final.analisar` em `final/dados/`: 9 válidas, código 0, sem avisos.
- `dados_old/` e `dados_exemplo/` validados e reportados (ver `CURRENT_STATE.md`).
- Dados, `dados_old/`, `dados_exemplo/`, `parcial/` e `resultados/` comparados com a entrega anterior: idênticos.

### Pendências
- Prioridade 2 (cálculos) e Prioridade 3 (pipeline, gráficos, relatórios e gravação).

## 2026-11-20 — Prioridade 2: cálculos científicos

### Alterações
- `final/periodos.py`: `construir_ciclos` (ciclos entre mergulhos consecutivos, massa no ponto médio com suporte, identificadores de posição), `interpolar_massa` (sem extrapolação, máscara explícita de domínio), `estatisticas_periodos` (desvio amostral, ausente com menos de 2 períodos), `periodos_por_janela` (todas as janelas listadas; status `sem_ciclos`/`sem_desvio`/`ok`).
- `final/massa.py`: `ajustar_linear` (MMQ, resíduos, R², erro padrão de `b`, diagnósticos `poucos_pontos`, `massa_constante`, `sem_graus_de_liberdade`), `taxa_de_perda` (taxa só para `b<0`), `ajustar_janelas` (uma linha por janela, sem misturar leituras).
- Testes: `tests/test_periodos_calculos.py`, `tests/test_massa_calculos.py` e uma integração somente leitura em `tests/test_dados_reais.py`.
- Atualizados `PROJECT.md` (9), `TASKS.md`, `CURRENT_STATE.md`, `HANDOFF.md` e READMEs.

### Verificações
- `python -m pytest`: 144 passed.
- Comparações independentes: `np.polyfit` (coeficientes) e fórmula matricial (erro padrão), com dados ruidosos fixos.
- Mutações: interpolação sem máscara de domínio, sinal da taxa invertido e desvio populacional — todas detectadas.
- Bugs encontrados pelos testes e corrigidos: divisão por zero com 2 leituras (agora `sem_graus_de_liberdade`); tratamento de `pd.NA` na agregação por janela.
- Nove conjuntos reais: somente leitura; cada filmagem gera n−1 ciclos e nenhum ciclo ou leitura se perde ao agregar por janela. Valores de referência em `CURRENT_STATE.md`.
- Dados e `parcial/` não alterados.

### Pendências
- Prioridade 3 (pipeline, gráficos, relatórios e gravação em `--saida`).

## 2026-11-20 — Prioridade 3: pipeline, gráficos, relatórios e lote na CLI

### Correção de dados (pelo pesquisador, verificada)
- `final/dados/agua_dia1/massa.csv`: 28 leituras (20,018–560,007 s) acrescidas de 0,1000 g; 580,007 s e 600,007 s inalteradas; tempos iguais. Nenhum outro arquivo de dados foi alterado. Efeito: salto de +0,0965 g em 560–580 s desaparece; R² global 0,24 → 0,96.

### Alterações
- `final/pipeline.py`: `processar_filmagem` orquestra uma filmagem a partir do dicionário validado; `t_fim` = maior instante de massa ou mergulhos; recusa saída dentro dos dados.
- `final/graficos.py`: `plotar_angulo_mergulhos`, `plotar_massa_ajuste`, `plotar_periodo_tempo`, `plotar_periodo_massa`, com API orientada a objetos do matplotlib (sem pyplot); `DadosInsuficientes(motivo)`.
- `final/relatorio.py`: `gravar_tabelas`, `montar_resumo_texto`, `gravar_resumo_texto` com precisão completa e proteção da pasta de origem.
- `final/analisar.py`: lote de processamento na CLI, com isolamento de falha de processamento (status `erro_processamento`). A mensagem de "não implementado" foi removida.
- Testes: `tests/test_saidas.py` e processamento real temporário em `tests/test_dados_reais.py`. Testes da CLI atualizados.
- Resultados gerados em `final/resultados/` para os nove conjuntos (99 arquivos).
- Atualizados `PROJECT.md` (7, 8, 9), `TASKS.md`, `CURRENT_STATE.md`, `HANDOFF.md` e READMEs.

### Verificações
- `python -m pytest`: 165 passed.
- Mutações: CSV arredondado, proteção da pasta de dados removida, gráfico sem dados não omitido — todas detectadas.
- Execução completa da CLI: 9 processadas, 0 falhas, código 0.
- Inspeção visual de figuras (agua_dia1) e conferência de tabelas contra cálculo direto.
- Dados brutos e parcial comparados byte a byte com o pacote recebido: sem divergência.

### Pendências
- Prioridade 4: validação ponta a ponta com revisão manual e documentação de execução e formatos.

## 2026-11-20 — Prioridade 4: qualidade, validação ponta a ponta e documentação

### Alterações
- `tests/test_dados_reais.py`: expandido com estrutura/qualidade (monotonia, massas positivas, contagem de ciclos sem suporte), regressão numérica dos nove conjuntos contra a tabela de referência de CURRENT_STATE, e teste ponta a ponta de agua_dia1 (amostras de ciclos, resumo, taxas, R² e gráficos).
- Criado `ai-context/REVISAO_QUALIDADE.md`: inventário estrutural das nove filmagens, avisos de validação, revisão manual amostral de agua_dia1 (primeiro/último ciclo, ajuste global, janelas), e limitações experimentais (R² baixos, desvios, movimento na balança, condições estáticas).
- Atualizados `TASKS.md` (Prioridade 4 concluída), `CURRENT_STATE.md`, `HANDOFF.md` e READMEs com o estado pós-P4 e a referência ao documento de revisão.

### Verificações
- `python -m pytest`: 168 passed (antes 165; +3 casos novos (estrutura, regressão, ponta a ponta) de dados reais).
- Regressão numérica: períodos, taxas, R² e resíduos dos nove conjuntos dentro das tolerâncias documentadas.
- Processamento de agua_dia1 em diretório temporário: 22 ciclos, taxa 0,00835 g/min, R² 0,964, resíduo máx. 0,0159 g; arquivos e gráficos presentes.
- Dados brutos e `parcial/` não alterados.

### Pendências
- Interpretação científica dos casos de baixo R² e comparação entre líquidos (fora do escopo de implementação do pipeline).

## 2026-11-20 — Correção de dados de coleta e reprocessamento

### Alterações (dados, pelo pesquisador)
- massa.csv: agua_dia3 (5 pts), alcool70_dia2 (8), alcool70_dia3 (9), alcool99_dia1 (6), alcool99_dia2 (14), alcool99_dia3 (9); Δ até 0,100 g.
- mergulhadas.csv: alcool70_dia1 57→36 eventos; alcool70_dia3 37→29; ajuste pontual em alcool70_dia2.
- Código não alterado.

### Alterações (repositório de trabalho)
- Dados substituídos pelos CSVs corrigidos; `final/resultados/` regenerado (99 arquivos).
- `tests/test_dados_reais.py`: REF_RESUMO atualizado.
- `CURRENT_STATE.md`, `REVISAO_QUALIDADE.md`, este LOG atualizados.

### Verificações
- `python -m pytest`: 168 passed.
- CLI: 9 processadas, 0 falhas, código 0.
- R² de todos os conjuntos ≥ 0,96 (antes vários < 0,8).
- Valores de referência conferidos amostra a amostra.

### Pendências
- Interpretação científica das taxas/períodos entre líquidos; exame de resíduos de alcool70_dia3 e desvio de alcool70_dia2.

## 2026-11-20 — Etapa 4: calor latente NIST, L·r com incerteza e comparação dia a dia

### Decisões do pesquisador
- Comparação principal dia a dia; variação entre dias à parte.
- Mistura "álcool 70%" = etanol a 70 % em massa (w/w); "álcool 99%" = isopropanol.
- Fonte do calor latente: NIST. Grandeza comparada com o período: L·r.
- Corrida piloto do relatório parcial excluída; mergulhos sem alteração; critério formal adiado.

### Alterações
- `final/constantes.py` (novo): propriedades NIST/JANAF a 298,15 K; pressão de vapor da água (JANAF), etanol e isopropanol (Antoine); L da mistura (primário: fração mássica do vapor, Raoult; alternativo: fração do líquido); quantil t; conversão L·r.
- `final/comparacao.py` (novo): tabelas e gráficos por dia e entre dias; hipóteses descritivas (ordens e inclinação log–log, n = 3).
- `final/massa.py`: IC95% de b e da taxa.
- `final/periodos.py`: IC95% da média dos períodos.
- `final/pipeline.py`: L, L·r com IC, colunas novas em massa_ajuste, massa_por_janela, resumo; gráfico exploratório período × massa removido.
- `final/graficos.py`: formatação fixa; figuras de comparação; ticks log legíveis.
- `final/relatorio.py`: resumo com formatos fixos e seção de calor latente/L·r.
- `final/analisar.py`: validação do nome do líquido; comparação ao fim do lote.
- `requirements.txt`: scipy ≥ 1.11; mínimos verificados em Python 3.10, 3.11 e 3.12.
- Testes: `test_constantes_incertezas.py`, `test_comparacao.py`, `test_referencia_etapa4.py`; testes existentes atualizados. Total 210.
- Documentação: PROJECT (6.5, 5, 7, 9), TASKS (Prioridade 5), CURRENT_STATE, HANDOFF, README raiz e `final/README.md`.

### Verificações
- `python -m pytest`: 210 passed.
- Referência independente das nove filmagens (taxa, IC95%, L, L·r): coincide, erro relativo ≤ 1e-9.
- Mutações: L primário trocado (detectado); quantil normal no lugar do t (3 testes); limites do IC invertidos (14 testes).
- Versões mínimas: 210 testes passam com numpy 1.26.4, pandas 2.1.4, matplotlib 3.8.4, scipy 1.11.4 e pytest 7.4.4 em Python 3.10.20, 3.11.15 e 3.12.3.
- Execução oficial: 9 processadas, 0 falhas, comparação gerada; saídas em `final/resultados/` (112 arquivos).
- Dados brutos, dados_old, dados_exemplo e parcial não modificados.

### Pendências
- Critério formal de mergulho e segundo anotador.
- Decisão sobre a forma da análise principal (dia a dia agregado ou global com dia como fator).
- Análise de sensibilidade (L alternativo, janelas, critério de mergulho).
- Pressão de vapor do isopropanol a 25 °C é extrapolação; dependência de L com T não corrigida.

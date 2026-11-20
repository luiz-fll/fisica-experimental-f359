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

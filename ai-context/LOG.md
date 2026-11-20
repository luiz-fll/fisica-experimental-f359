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

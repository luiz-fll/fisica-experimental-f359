# Plano de desenvolvimento

Este plano reflete o estado observado em 2026-11-20. O pedido explícito do usuário para cada execução define o escopo; a existência de tarefas pendentes não autoriza executá-las todas.

## Regras

- Marcar como concluído somente após implementação e verificação.
- Não confundir arquivo criado com funcionalidade implementada.
- Não alterar dados brutos nem `parcial/`.
- Atualizar prioridades quando dependências mudarem.
- Se uma tarefa for bloqueada, registrar o bloqueio concreto.

## Prioridade 0 — Fundação do projeto

- [x] Definir versão mínima de Python e dependências; criar `requirements.txt` ou `pyproject.toml`. *(Python 3.10+ declarado; desenvolvido e testado somente em 3.12.3. Versões mínimas das bibliotecas são estimativas não verificadas. Ver `requirements.txt`.)*
- [x] Definir contratos de entrada/saída e funções dos seis módulos em `final/`. *(Assinaturas e docstrings; implementação pendente, ver `PROJECT.md` seção 9.)*
- [x] Definir convenção de limites das janelas. *(Implementada em `final/periodos.py`; a última janela absorve o resto do ensaio, decisão do pesquisador, ver `PROJECT.md` 6.3.)*
- [x] Definir mínimo de pontos para ajustes locais e política de janelas insuficientes. *(Constantes em `massa.py` e `periodos.py`. A aplicação da política depende da implementação das funções de ajuste.)*
- [x] Criar estrutura `tests/` e configurar execução de testes. *(`pytest.ini`, 35 testes passando.)*

## Prioridade 1 — Entrada e validação

- [x] Implementar CLI em `final/analisar.py`. *(Validação e relatório implementados; gravação de resultados e processamento ficam nas Prioridades 2 e 3.)*
- [x] Implementar descoberta das subpastas de `final/dados/`.
- [x] Implementar leitura dos cabeçalhos reais: `tempo_seg`, `angulo_deg`, `massa_g`, `liquido`, `dia`, `temperatura_c`, `umidade_pct`.
- [x] Validar os quatro CSVs por filmagem sem modificá-los.
- [x] Garantir isolamento e continuidade do lote após erro individual.

*Verificação: 85 testes passando; os nove conjuntos reais saem válidos, com código 0 e sem avisos.*

## Prioridade 2 — Cálculos científicos

- [x] Implementar períodos entre eventos manuais de `mergulhadas.csv`.
- [x] Implementar interpolação da massa no ponto médio, sem extrapolação.
- [x] Implementar estatísticas globais e por janela dos períodos.
- [x] Implementar ajuste linear global da massa.
- [x] Implementar resíduos, taxas e diagnósticos.
- [x] Implementar ajustes locais por janelas fixas.

*Verificação: 144 testes passando, incluindo comparações com `np.polyfit` e com a fórmula matricial do erro padrão, três mutações nas regras críticas detectadas, e uma integração somente leitura sobre os nove conjuntos reais. Dois bugs encontrados pelos testes e corrigidos: divisão por zero com duas leituras; ausência de tratamento de ciclos fora do domínio da massa.*

## Prioridade 3 — Pipeline e saídas

- [x] Implementar orquestração em `final/pipeline.py`.
- [x] Implementar gráficos em `final/graficos.py`.
- [x] Implementar tabelas e resumos em `final/relatorio.py`.
- [x] Integrar execução em lote pela CLI.
- [x] Garantir que resultados sejam gravados em diretório separado dos dados.

*Verificação: 165 testes passando; execução completa sobre os nove conjuntos reais (9 processadas, 0 falhas, 99 arquivos); três mutações nas regras de precisão, proteção dos dados e omissão de gráficos detectadas; inspeção visual dos gráficos.*

## Prioridade 4 — Qualidade e validação

- [x] Criar testes unitários para períodos e interpolação. *(`tests/test_periodos_calculos.py`)*
- [x] Criar testes para ajustes lineares e conversão de unidades. *(`tests/test_massa_calculos.py`)*
- [x] Criar testes para janelas e dados insuficientes. *(`test_janelas.py`, `test_massa_calculos.py`, `test_periodos_calculos.py`)*
- [x] Criar testes de isolamento e falha individual. *(Cobertos para a camada de validação em `tests/test_analisar.py`.)*
- [x] Validar estrutura/qualidade dos dados reais sem alterar os originais. *(`tests/test_dados_reais.py`: monotonia, massas positivas, contagem de ciclos sem suporte, avisos documentados em `REVISAO_QUALIDADE.md`.)*
- [x] Validar uma filmagem real ponta a ponta e revisar amostras manualmente. *(`agua_dia1`: primeiro/último ciclo, resumo, taxas e R² conferidos contra cálculo direto; registro em `ai-context/REVISAO_QUALIDADE.md`.)*
- [x] Documentar dependências, execução, formatos e limitações. *(READMEs, `REVISAO_QUALIDADE.md`, seções de limitações no `resumo.txt` e em PROJECT.md.)*

*Verificação: 168 testes passando; regressão numérica dos nove conjuntos contra a tabela de referência; amostra ponta a ponta de agua_dia1; dados brutos intactos.*

## Prioridade 5 — Etapa 4: calor latente, L·r com incerteza e comparação dia a dia

- [x] Substituir a comparação com massa por L·r (produto do calor latente pela taxa). *(`final/constantes.py`, `pipeline.py`)*
- [x] Calor latente de NIST para água, etanol e isopropanol; mistura 70 % w/w por composição do vapor (Raoult), com alternativo como sensibilidade. *(`constantes.py`)*
- [x] IC95% da inclinação, da taxa, da média dos períodos e de L·r. *(`massa.py`, `periodos.py`, `pipeline.py`)*
- [x] Formatação numérica fixa em gráficos e textos (corrige a leitura da taxa do isopropanol).
- [x] Comparação principal dia a dia, com condições do próprio dia; variação entre dias à parte. *(`final/comparacao.py`)*
- [x] Gráficos de comparação: massa, períodos, τ × L·r (log–log), taxas por janela, e variação entre dias. *(`final/graficos.py`)*
- [x] Remoção do gráfico exploratório período × massa (substituído pela comparação com L·r).
- [x] Validação do nome do líquido em `condicoes.csv`.
- [x] Referência independente das grandezas da etapa 4 sobre os nove conjuntos reais.
- [x] Versões mínimas verificadas em Python 3.10, 3.11 e 3.12 (scipy incluído).

*Verificação: 210 testes passando; referência independente coincide (rel. 1e-9); três mutações detectadas; execução oficial em `final/resultados/` (112 arquivos).*

**Não feito (adiado pelo pesquisador):** critério formal de mergulho e segundo anotador; análise de sensibilidade (L alternativo, janelas, critério); decisão entre análise dia a dia agregada e global com dia como fator.

## Bloqueios e decisões pendentes

- **Nenhum bloqueio de implementação.** Interpretação dos cálculos é responsabilidade do pesquisador: inclinações não negativas não são taxas (ver `PROJECT.md` 6.4).
- **Decisões de entrada que podem ser revistas:** `--diretorio` e `--saida` têm padrão em `final/`; a janela padrão é 200 s; uma filmagem com menos de 2 mergulhos é inválida (não só sem períodos).
- **Dados:** os problemas de qualidade (saltos de massa já corrigidos em agua_dia1, critério de anotação, sincronização temporal, R² baixos em alguns álcoois) estão registrados em `ai-context/REVISAO_QUALIDADE.md` e não são verificados pela validação de formato.

## Concluído nesta revisão documental

- [x] Inventariar a estrutura atual e alinhar a documentação aos caminhos reais em `final/`.
- [x] Registrar os nove conjuntos de dados e os cabeçalhos observados.
- [x] Distinguir módulos vazios de `final/teste.py`, que é apenas um script estrutural.
- [x] Atualizar instruções para agentes e proteger dados e histórico.

## Em andamento

Nenhuma. Etapa 4 concluída; próximas ações estão em `CURRENT_STATE.md`.

## Bloqueios

Nenhum.

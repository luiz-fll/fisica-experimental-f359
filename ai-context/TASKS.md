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

- [ ] Implementar orquestração em `final/pipeline.py`.
- [ ] Implementar gráficos em `final/graficos.py`.
- [ ] Implementar tabelas e resumos em `final/relatorio.py`.
- [ ] Integrar execução em lote pela CLI.
- [ ] Garantir que resultados sejam gravados em diretório separado dos dados.

## Prioridade 4 — Qualidade e validação

- [x] Criar testes unitários para períodos e interpolação. *(`tests/test_periodos_calculos.py`)*
- [x] Criar testes para ajustes lineares e conversão de unidades. *(`tests/test_massa_calculos.py`)*
- [x] Criar testes para janelas e dados insuficientes. *(`test_janelas.py`, `test_massa_calculos.py`, `test_periodos_calculos.py`)*
- [x] Criar testes de isolamento e falha individual. *(Cobertos para a camada de validação em `tests/test_analisar.py`.)*
- [ ] Validar estrutura/qualidade dos dados reais sem alterar os originais.
- [ ] Validar uma filmagem real ponta a ponta e revisar amostras manualmente.
- [ ] Documentar dependências, execução, formatos e limitações.

## Bloqueios e decisões pendentes

- **Nenhum bloqueio de implementação.** Interpretação dos cálculos é responsabilidade do pesquisador: inclinações não negativas não são taxas (ver `PROJECT.md` 6.4).
- **Decisões de entrada que podem ser revistas:** `--diretorio` e `--saida` têm padrão em `final/`; a janela padrão é 200 s; uma filmagem com menos de 2 mergulhos é inválida (não só sem períodos).
- **Dados:** os problemas de qualidade (saltos de massa, critério de anotação, sincronização temporal) estão registrados em `revisao_dados_e_plano.md` e não são verificados pela validação de formato.

## Concluído nesta revisão documental

- [x] Inventariar a estrutura atual e alinhar a documentação aos caminhos reais em `final/`.
- [x] Registrar os nove conjuntos de dados e os cabeçalhos observados.
- [x] Distinguir módulos vazios de `final/teste.py`, que é apenas um script estrutural.
- [x] Atualizar instruções para agentes e proteger dados e histórico.

## Em andamento

Nenhuma. Prioridade 2 (cálculos) concluída; próxima etapa: Prioridade 3 (pipeline, gráficos, relatórios e gravação).

## Bloqueios

Nenhum bloqueio externo identificado. O desenvolvimento está pendente, não bloqueado: os nove conjuntos em `final/dados/` possuem os quatro CSVs esperados, mas a implementação e os testes ainda não existem.

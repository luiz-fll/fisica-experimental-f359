# Plano de desenvolvimento

Este plano reflete o estado observado em 2026-11-20. O pedido explícito do usuário para cada execução define o escopo; a existência de tarefas pendentes não autoriza executá-las todas.

## Regras

- Marcar como concluído somente após implementação e verificação.
- Não confundir arquivo criado com funcionalidade implementada.
- Não alterar dados brutos nem `parcial/`.
- Atualizar prioridades quando dependências mudarem.
- Se uma tarefa for bloqueada, registrar o bloqueio concreto.

## Prioridade 0 — Fundação do projeto

- [ ] Definir versão mínima de Python e dependências; criar `requirements.txt` ou `pyproject.toml`.
- [ ] Definir contratos de entrada/saída e funções dos seis módulos em `final/`.
- [ ] Definir convenção de limites das janelas.
- [ ] Definir mínimo de pontos para ajustes locais e política de janelas insuficientes.
- [ ] Criar estrutura `tests/` e configurar execução de testes.

## Prioridade 1 — Entrada e validação

- [ ] Implementar CLI em `final/analisar.py`.
- [ ] Implementar descoberta das subpastas de `final/dados/`.
- [ ] Implementar leitura dos cabeçalhos reais: `tempo_seg`, `angulo_deg`, `massa_g`, `liquido`, `dia`, `temperatura_c`, `umidade_pct`.
- [ ] Validar os quatro CSVs por filmagem sem modificá-los.
- [ ] Garantir isolamento e continuidade do lote após erro individual.

## Prioridade 2 — Cálculos científicos

- [ ] Implementar períodos entre eventos manuais de `mergulhadas.csv`.
- [ ] Implementar interpolação da massa no ponto médio, sem extrapolação.
- [ ] Implementar estatísticas globais e por janela dos períodos.
- [ ] Implementar ajuste linear global da massa.
- [ ] Implementar resíduos, taxas e diagnósticos.
- [ ] Implementar ajustes locais por janelas fixas.

## Prioridade 3 — Pipeline e saídas

- [ ] Implementar orquestração em `final/pipeline.py`.
- [ ] Implementar gráficos em `final/graficos.py`.
- [ ] Implementar tabelas e resumos em `final/relatorio.py`.
- [ ] Integrar execução em lote pela CLI.
- [ ] Garantir que resultados sejam gravados em diretório separado dos dados.

## Prioridade 4 — Qualidade e validação

- [ ] Criar testes unitários para períodos e interpolação.
- [ ] Criar testes para ajustes lineares e conversão de unidades.
- [ ] Criar testes para janelas e dados insuficientes.
- [ ] Criar testes de isolamento e falha individual.
- [ ] Validar estrutura/qualidade dos dados reais sem alterar os originais.
- [ ] Validar uma filmagem real ponta a ponta e revisar amostras manualmente.
- [ ] Documentar dependências, execução, formatos e limitações.

## Concluído nesta revisão documental

- [x] Inventariar a estrutura atual e alinhar a documentação aos caminhos reais em `final/`.
- [x] Registrar os nove conjuntos de dados e os cabeçalhos observados.
- [x] Distinguir módulos vazios de `final/teste.py`, que é apenas um script estrutural.
- [x] Atualizar instruções para agentes e proteger dados e histórico.

## Em andamento

Nenhuma tarefa de implementação registrada.

## Bloqueios

Nenhum bloqueio externo identificado. O desenvolvimento está pendente, não bloqueado: os nove conjuntos em `final/dados/` possuem os quatro CSVs esperados, mas a implementação e os testes ainda não existem.

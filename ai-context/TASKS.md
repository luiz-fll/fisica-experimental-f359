# Plano de desenvolvimento

Este arquivo acompanha o progresso do software final. O prompt do usuário define a tarefa da execução; este documento não deve ser interpretado como autorização para executar todas as tarefas pendentes de uma vez.

## Regras de atualização
- Marcar uma tarefa como concluída somente após implementação e verificação.
- Mover tarefa para “Em andamento” quando o trabalho começar.
- Registrar bloqueios concretos.
- Não alterar o histórico de `parcial/`.
- Reordenar prioridades quando dependências mudarem.

## Prioridade 0 — Preparação e contrato
- [ ] Confirmar estrutura definitiva de diretórios e localização dos seis módulos na raiz.
- [ ] Definir e documentar dependências e versão mínima de Python.
- [ ] Definir contratos de funções entre os seis módulos.
- [ ] Definir política de limites das janelas e mínimo de pontos para ajustes locais.

## Prioridade 1 — Entrada e validação
- [ ] Implementar CLI em `analisar.py`.
- [ ] Implementar descoberta das subpastas de filmagem.
- [ ] Implementar leitura e validação dos quatro CSVs.
- [ ] Garantir isolamento entre filmagens e continuidade do lote após erro individual.

## Prioridade 2 — Cálculos científicos
- [ ] Implementar cálculo dos períodos em `periodos.py`.
- [ ] Implementar interpolação da massa nos pontos médios dos ciclos, sem extrapolação.
- [ ] Implementar estatísticas globais e por janela de período.
- [ ] Implementar ajuste linear global da massa em `massa.py`.
- [ ] Implementar resíduos e diagnósticos do ajuste.
- [ ] Implementar ajustes locais por janelas fixas.

## Prioridade 3 — Saídas
- [ ] Implementar gráficos em `graficos.py`.
- [ ] Implementar exportação de tabelas e resumo em `relatorio.py`.
- [ ] Implementar orquestração de uma filmagem em `pipeline.py`.
- [ ] Integrar execução em lote pela CLI.

## Prioridade 4 — Qualidade e validação
- [ ] Criar testes unitários para períodos e interpolação.
- [ ] Criar testes para ajustes lineares e conversão de unidades.
- [ ] Criar testes para janelas e dados insuficientes.
- [ ] Criar teste de isolamento e falha individual de filmagem.
- [ ] Validar uma filmagem real completa e comparar amostras manualmente.
- [ ] Documentar execução, formatos e limitações no README.

## Em andamento
- Nenhuma tarefa registrada.

## Bloqueios
- Os dados atualmente disponíveis no diretório `final/dados/` não incluem necessariamente todos os quatro CSVs requeridos por filmagem. A análise completa depende de completar os dados ausentes.

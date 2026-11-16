# Análise do pássaro bebedor

Projeto de análise de dados do experimento sobre a relação entre o líquido externo, a evaporação e o período do ciclo de mergulho do pássaro bebedor.

## Contexto para agentes
Antes de trabalhar no código, leia `AGENTS.md` e os documentos em `ai-context/`. A especificação técnica está em `ai-context/PROJECT.md`; o contexto científico está em `ai-context/EXPERIMENT.md`.

**A pasta `parcial/` é um registro histórico imutável do relatório parcial. Não deve ser modificada nem usada como base de código para a implementação final.**

## Estrutura prevista
Os módulos da implementação final ficam na raiz:
`analisar.py`, `pipeline.py`, `periodos.py`, `massa.py`, `graficos.py` e `relatorio.py`.

Os dados são organizados em subpastas independentes dentro de `dados/`. Cada filmagem deve conter quatro CSVs: `tracker.csv`, `massa.csv`, `mergulhadas.csv` e `condicoes.csv`.

## Estado
A implementação final e os testes ainda precisam ser desenvolvidos. Consulte `ai-context/CURRENT_STATE.md` e `ai-context/TASKS.md`.

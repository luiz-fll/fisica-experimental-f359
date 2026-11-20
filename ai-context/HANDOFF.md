# Handoff — transferência de contexto

## Objetivo

Desenvolver o pipeline reprodutível de análise do pássaro bebedor, mantendo integridade dos dados e metodologia científica explícita.

## Regras invariáveis

- `parcial/` é histórico imutável. Não inspecionar nem alterar, salvo pedido explícito de comparação/contexto histórico.
- Não alterar arquivos de dados em `final/dados/`, `final/dados_exemplo/` ou `final/dados_old/`.
- A implementação final fica em `final/`; não mover módulos para a raiz.
- Cada subpasta de `final/dados/` é uma filmagem independente.
- Eventos de mergulho são selecionados manualmente em `mergulhadas.csv`; não detectar automaticamente cada oscilação.
- Períodos são diferenças entre tempos consecutivos de eventos.
- Massa pode ser interpolada no ponto médio de cada ciclo, sem extrapolação.
- Ajuste principal inicial da massa é linear global, acompanhado de resíduos e diagnósticos.
- Ajustes locais usam janelas fixas configuráveis, padrão inicial de 200 s; não escolher janelas para forçar linearidade.
- Se a inclinação de massa for negativa, a taxa positiva de perda é \(-b\) g/s ou \(-60b\) g/min.

## Estrutura e dados verificados

- Os seis módulos planejados estão em `final/` e estão vazios.
- `final/teste.py` é apenas um script estrutural; não é suíte de testes nem pipeline.
- `final/dados/` contém nove filmagens reais: `agua_dia1..3`, `alcool70_dia1..3`, `alcool99_dia1..3`.
- Todas as nove têm `tracker.csv`, `massa.csv`, `mergulhadas.csv` e `condicoes.csv`.
- `final/dados_exemplo/filmagem_exemplo/` contém um conjunto reduzido de exemplo.
- `final/dados_old/` contém uma cópia anterior dos CSVs e não é entrada padrão.
- Cabeçalhos reais: `tracker.csv` = `tempo_seg,angulo_deg`; `massa.csv` = `tempo_seg,massa_g`; `mergulhadas.csv` = `tempo_seg,angulo_deg`; `condicoes.csv` = `liquido,dia,temperatura_c,umidade_pct`.
- Não há `evento_id` em `mergulhadas.csv`; identificadores podem ser derivados em memória/saída, sem editar a fonte.
- Prioridade 2 concluída (cálculos): `periodos.py` e `massa.py` implementados e testados (144 testes). Pipeline, gráficos e relatórios ainda são contratos.
- Prioridade 1 concluída (validação): `final/analisar.py` com CLI, descoberta, leitura e validação (`tests/test_analisar.py`).
- Fundação concluída em 2026-11-20: `requirements.txt`, `requirements-dev.txt`, `pytest.ini` e `tests/` (85 testes no total). A convenção de janelas está implementada em `periodos.py`; `periodos.py` e `massa.py` têm apenas contratos, exceto as janelas; `pipeline.py`, `graficos.py` e `relatorio.py` têm apenas contratos (`NotImplementedError`).
- Decisões de continuidade: origem temporal 0 s; janelas `[início, fim)`; a última absorve o resto do ensaio, `[(N-1)·L, t_fim]`, com `N = max(1, floor(t_fim/L))`; mínimo de 3 leituras para ajuste (5 recomendado); mínimo de 2 mergulhos para período e 2 períodos para desvio-padrão.
- Imports: `from final.<modulo> import ...`; execução com `python -m final.analisar`.

## Próxima sequência sugerida

1. Prioridade 3: `pipeline.py`, `graficos.py`, `relatorio.py`, integração em lote na CLI e gravação em `--saida`.
2. Prioridade 4: validação ponta a ponta e revisão amostral das saídas.

## Como retomar

1. Ler `AGENTS.md`, `ai-context/CURRENT_STATE.md`, `ai-context/TASKS.md`, `ai-context/PROJECT.md` e `ai-context/EXPERIMENT.md`.
2. Conferir novamente o estado real do código e dos dados; este handoff também pode ficar desatualizado.
3. Executar somente a tarefa solicitada e suas dependências necessárias.
4. Não marcar itens como concluídos sem implementação e verificação.
5. Ao concluir, atualizar `CURRENT_STATE.md`, `TASKS.md` e acrescentar uma entrada a `LOG.md`.

Este documento resume decisões e contexto de continuidade; não substitui inspeção do repositório.

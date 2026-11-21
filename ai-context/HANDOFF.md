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

- Os módulos em `final/` estão implementados e testados (Prioridades 0–4 e etapa 4), incluindo `constantes.py` e `comparacao.py`.
- `final/teste.py` é apenas um script estrutural; não é suíte de testes nem pipeline.
- `final/dados/` contém nove filmagens reais: `agua_dia1..3`, `alcool70_dia1..3`, `alcool99_dia1..3`.
- Todas as nove têm `tracker.csv`, `massa.csv`, `mergulhadas.csv` e `condicoes.csv`.
- `final/dados_exemplo/filmagem_exemplo/` contém um conjunto reduzido de exemplo.
- `final/dados_old/` contém uma cópia anterior dos CSVs e não é entrada padrão.
- Cabeçalhos reais: `tracker.csv` = `tempo_seg,angulo_deg`; `massa.csv` = `tempo_seg,massa_g`; `mergulhadas.csv` = `tempo_seg,angulo_deg`; `condicoes.csv` = `liquido,dia,temperatura_c,umidade_pct`.
- Não há `evento_id` em `mergulhadas.csv`; identificadores podem ser derivados em memória/saída, sem editar a fonte.
- Etapa 4 concluída (2026-11-20): taxa, L e L·r com IC95%; comparação dia a dia (principal) e entre dias; calor latente NIST (`final/constantes.py`); líquidos: `agua`, `alcool 70%` = etanol 70 % w/w, `alcool 99%` = isopropanol; corrida piloto excluída; critério de mergulho adiado. Detalhes em `CURRENT_STATE.md` e `PROJECT.md` 6.5.
- Prioridade 4 concluída: testes de estrutura/qualidade e regressão numérica dos dados reais; revisão ponta a ponta de `agua_dia1`; documentação em `REVISAO_QUALIDADE.md`.
- Prioridade 3 concluída (pipeline e saídas); resultados oficiais atuais em `final/resultados/` (112 arquivos, incluindo `comparacao/`).
- Correção de dados pelo pesquisador: `agua_dia1/massa.csv` (28 leituras +0,1000 g, 20–560 s). Ver `CURRENT_STATE.md`.
- Prioridade 2 concluída (cálculos): `periodos.py` e `massa.py` implementados e testados.
- Prioridade 1 concluída (validação): `final/analisar.py` com CLI, descoberta, leitura e validação.
- Fundação (Prioridade 0): `requirements.txt`, `requirements-dev.txt`, `pytest.ini` e `tests/`.
- Decisões de continuidade: origem temporal 0 s; janelas `[início, fim)`; a última absorve o resto do ensaio, `[(N-1)·L, t_fim]`, com `N = max(1, floor(t_fim/L))`; mínimo de 3 leituras para ajuste (5 recomendado); mínimo de 2 mergulhos para período e 2 períodos para desvio-padrão.
- Imports: `from final.<modulo> import ...`; execução com `python -m final.analisar`.

## Próxima sequência sugerida

1. Formalizar o critério de mergulho (com segundo anotador e concordância), quando o pesquisador decidir.
2. Decidir a análise principal: dia a dia agregado, ou global com dia como fator.
3. Análise de sensibilidade: L alternativo da mistura, janelas de 100/200/300 s, critério de mergulho.

## Como retomar

1. Ler `AGENTS.md`, `ai-context/CURRENT_STATE.md`, `ai-context/TASKS.md`, `ai-context/PROJECT.md` e `ai-context/EXPERIMENT.md`.
2. Conferir novamente o estado real do código e dos dados; este handoff também pode ficar desatualizado.
3. Executar somente a tarefa solicitada e suas dependências necessárias.
4. Não marcar itens como concluídos sem implementação e verificação.
5. Ao concluir, atualizar `CURRENT_STATE.md`, `TASKS.md` e acrescentar uma entrada a `LOG.md`.

Este documento resume decisões e contexto de continuidade; não substitui inspeção do repositório.

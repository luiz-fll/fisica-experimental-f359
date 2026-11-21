# Estado atual do projeto

> Estado verificado em 2026-11-20, após correção de dados de coleta pelo pesquisador e reprocessamento completo. Atualizar após cada execução que alterar o repositório.

## Situação geral

Prioridades 0 a 4 concluídas. O pesquisador corrigiu erros de coleta em vários CSVs de massa e de mergulhadas (sem alteração de código). Pipeline reexecutado: 9 filmagens processadas, 0 falhas, 99 arquivos em `final/resultados/`. Testes de regressão atualizados para os novos valores de referência.

Verificado: `python -m pytest` → 168 passed; `python -m final.analisar` sobre `final/dados/` sai com código 0.

## Correções de dados (pelo pesquisador)

Comparação com a versão anterior do pacote:

| Filmagem | Arquivo | Mudança |
|---|---|---|
| agua_dia3 | massa.csv | 5 leituras alteradas (Δ máx. 0,010 g) |
| alcool70_dia1 | mergulhadas.csv | 57 → 36 eventos (remoção de anotações incorretas) |
| alcool70_dia2 | massa.csv | 8 leituras alteradas (Δ máx. 0,100 g) |
| alcool70_dia2 | mergulhadas.csv | ajuste pontual |
| alcool70_dia3 | massa.csv | 9 leituras alteradas (Δ máx. 0,100 g) |
| alcool70_dia3 | mergulhadas.csv | 37 → 29 eventos |
| alcool99_dia1 | massa.csv | 6 leituras alteradas (Δ máx. 0,100 g) |
| alcool99_dia2 | massa.csv | 14 leituras alteradas (Δ máx. 0,100 g) |
| alcool99_dia3 | massa.csv | 9 leituras alteradas (Δ máx. 0,100 g) |

Inalterados: agua_dia1, agua_dia2 (todos os CSVs); todos os `tracker.csv` e `condicoes.csv`.

Efeito principal: os R² baixos dos álcoois desaparecem; as taxas e períodos de `alcool70_dia1` e `alcool70_dia3` mudam pela limpeza das anotações de mergulho.

## Resultados gerados (valores de referência — pós-correção)

| Filmagem | Ciclos | Sem massa | Período médio (s) | Desvio (s) | Taxa global (g/min) | R² global | Resíduo máx. (g) |
|---|---:|---:|---:|---:|---:|---:|---:|
| agua_dia1 | 22 | 0 | 25,59 | 3,92 | 0,0084 | 0,964 | 0,0159 |
| agua_dia2 | 25 | 0 | 23,20 | 4,49 | 0,0070 | 0,967 | 0,0128 |
| agua_dia3 | 25 | 0 | 22,29 | 4,98 | 0,0071 | 0,974 | 0,0117 |
| alcool70_dia1 | 35 | 2 | 16,97 | 6,57 | 0,0283 | 0,976 | 0,0345 |
| alcool70_dia2 | 20 | 0 | 25,92 | 9,38 | 0,0207 | 0,964 | 0,0246 |
| alcool70_dia3 | 28 | 1 | 21,03 | 7,99 | 0,0312 | 0,970 | 0,0495 |
| alcool99_dia1 | 35 | 1 | 16,67 | 4,05 | 0,0355 | 0,982 | 0,0306 |
| alcool99_dia2 | 33 | 2 | 18,16 | 5,28 | 0,0318 | 0,986 | 0,0315 |
| alcool99_dia3 | 31 | 2 | 18,76 | 6,09 | 0,0288 | 0,984 | 0,0235 |

Observações:

- Todos os R² globais ficaram ≥ 0,96 (antes vários < 0,8).
- `alcool70_dia2` ainda tem desvio de período elevado (~9,4 s); a taxa e o R² melhoraram bastante com a correção de massa.
- Ciclos sem massa interpolada continuam associados a pontos médios após ~600 s.
- Nenhum gráfico omitido.

## Estrutura de código

Inalterada em relação à Prioridade 4. Módulos em `final/`; 168 testes em `tests/`.

## Saídas por filmagem

Em `final/resultados/<id>/`: `periodos.csv`, `massa_ajuste.csv`, `massa_residuos.csv`, `massa_por_janela.csv`, `periodo_por_janela.csv`, `resumo.csv`, `resumo.txt` e quatro PNG.

## Dados

- `final/dados/`: versão corrigida pelo pesquisador (esta execução).
- `final/dados_old/`, `final/dados_exemplo/`, `parcial/`: não modificados pelo software.
- `final/resultados/`: regenerado a partir dos dados corrigidos.

## Documentação de qualidade

- `ai-context/REVISAO_QUALIDADE.md`: atualizado com a correção e os novos números.
- Testes de regressão em `tests/test_dados_reais.py` usam a tabela acima.

## Próximas etapas recomendadas

1. Revisão científica das taxas e períodos entre líquidos (água × álcool 70% × álcool 99%).
2. Examinar resíduos de `alcool70_dia3` (resíduo máx. ainda ~0,05 g) e o desvio de período de `alcool70_dia2`.
3. Qualquer comparação formal entre condições fica a cargo do pesquisador.

## Limites

`parcial/` permanece histórico imutável. Dados brutos não devem ser modificados pelo software.

## Última atualização

2026-11-20. Reprocessamento após correção de coleta (massa e mergulhadas) pelo pesquisador.

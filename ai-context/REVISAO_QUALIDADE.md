# Revisão de qualidade dos dados e validação ponta a ponta

Documento atualizado em 2026-11-20 após correção de erros de coleta pelo
pesquisador e reprocessamento completo. Não altera arquivos de dados.

## 1. Correções aplicadas pelo pesquisador

| Filmagem | Arquivo | Alteração |
|---|---|---|
| agua_dia3 | massa.csv | 5 leituras (Δ máx. 0,010 g) |
| alcool70_dia1 | mergulhadas.csv | 57 → 36 eventos |
| alcool70_dia2 | massa.csv | 8 leituras (Δ máx. 0,100 g) |
| alcool70_dia2 | mergulhadas.csv | ajuste pontual |
| alcool70_dia3 | massa.csv | 9 leituras (Δ máx. 0,100 g) |
| alcool70_dia3 | mergulhadas.csv | 37 → 29 eventos |
| alcool99_dia1 | massa.csv | 6 leituras (Δ máx. 0,100 g) |
| alcool99_dia2 | massa.csv | 14 leituras (Δ máx. 0,100 g) |
| alcool99_dia3 | massa.csv | 9 leituras (Δ máx. 0,100 g) |

agua_dia1 e agua_dia2 permanecem iguais à versão anterior (já corrigida
anteriormente em massa de agua_dia1). Tracker e condições inalterados.

## 2. Estrutura dos nove conjuntos (pós-correção)

| Filmagem | Tracker (pts) | Massa (pts) | Mergulhos | Avisos de formato |
|---|---:|---:|---:|---|
| agua_dia1 | ~18215 | 30 | 23 | 1 mergulho fora do intervalo de massa |
| agua_dia2 | ~18505 | 30 | 26 | 1 mergulho fora do intervalo de massa |
| agua_dia3 | ~18180 | 30 | 26 | nenhum |
| alcool70_dia1 | ~18215 | 30 | 36 | 4 mergulhos fora do intervalo de massa |
| alcool70_dia2 | ~18084 | 30 | 21 | nenhum |
| alcool70_dia3 | ~17824 | 30 | 29 | 1 mergulho fora do intervalo de massa |
| alcool99_dia1 | ~18043 | 30 | 36 | 2 mergulhos fora do intervalo de massa |
| alcool99_dia2 | ~18296 | 30 | 34 | 3 mergulhos fora do intervalo de massa |
| alcool99_dia3 | ~17691 | 30 | 32 | 3 mergulhos fora do intervalo de massa |

Todos `status=valida`. Massas positivas; tempos monotônicos.

## 3. Resultados globais (pós-correção)

| Filmagem | Ciclos | Sem massa | Período médio (s) | Desvio (s) | Taxa (g/min) | R² | Resid máx (g) |
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

Comparação com a versão anterior: os R² de alcool70_dia2 (0,67),
alcool70_dia3 (0,71), alcool99_dia2 (0,78) e alcool99_dia3 (0,67) subiram
para ≥ 0,96. A limpeza de mergulhos em alcool70_dia1 e alcool70_dia3
reduziu o número de ciclos e alterou médias/desvios de período.

## 4. Validação ponta a ponta — agua_dia1 (inalterada nesta correção)

- 22 ciclos; primeiro T = 18,52 s; último dentro do domínio de massa.
- Taxa 0,00835 g/min; R² 0,964; resíduo máx. 0,0159 g.
- Três janelas de 200 s; todos os pontos contabilizados.
- Saídas completas (11 arquivos) geradas sem omissão de gráficos.

## 5. Observações restantes para interpretação

- Ciclos sem massa interpolada: ponto médio após a última leitura de massa.
- `alcool70_dia2`: desvio de período ainda alto (~9,4 s); R² e taxa
  melhoraram com a correção de massa.
- `alcool70_dia3`: resíduo máximo ainda ~0,05 g — examinar gráfico de
  resíduos.
- Condições ambientais: um registro por filmagem.
- O software não descarta pontos nem corrige anotações; apenas reporta
  avisos de domínio e diagnósticos de ajuste.

## 6. Proteção e testes

- Nenhuma escrita em `final/dados/`, `dados_exemplo/`, `dados_old/` ou
  `parcial/` pelo pipeline.
- `tests/test_dados_reais.py`: regressão numérica atualizada para a tabela
  da seção 3; estrutura, monotonia e ponta a ponta de agua_dia1.

Execução: `python -m pytest tests/test_dados_reais.py`.

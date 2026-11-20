# Estado atual do projeto

> Estado verificado em 2026-11-20, após a Prioridade 2 (cálculos científicos). Atualizar após cada execução que alterar o repositório.

## Situação geral

Prioridades 0, 1 e 2 concluídas. A CLI valida as filmagens e reporta erros e avisos. Os cálculos científicos existem como funções testadas, mas ainda não são executados pela CLI nem gravados em disco: a orquestração (`pipeline.py`), os gráficos, os relatórios e a gravação em `--saida` são a Prioridade 3.

Verificado: `python -m final.analisar` sobre `final/dados/` sai com código 0; as nove filmagens são válidas, sem erros nem avisos.

## Estrutura de código

- `final/analisar.py`: **implementado** — CLI, descoberta, leitura e validação (Prioridade 1).
- `final/periodos.py`: **implementado** — janelas (`definir_limites_janelas`, `atribuir_janela`), ciclos (`construir_ciclos`), interpolação sem extrapolação (`interpolar_massa`), estatísticas (`estatisticas_periodos`) e agregação por janela (`periodos_por_janela`).
- `final/massa.py`: **implementado** — ajuste linear (`ajustar_linear`), taxas com sinal (`taxa_de_perda`) e ajustes por janela (`ajustar_janelas`).
- `final/pipeline.py`, `final/graficos.py`, `final/relatorio.py`: contratos documentados; `NotImplementedError`.
- `final/teste.py`: script estrutural legado, inalterado.
- `tests/`: 144 testes.
  - `test_analisar.py`, `test_janelas.py`, `test_politicas.py`, `test_estrutura.py`: validação, janelas e importação.
  - `test_periodos_calculos.py` e `test_massa_calculos.py`: cálculos sintéticos. Comparações com `np.polyfit` e com a fórmula matricial do erro padrão, casos de domínio, mínimos e sinais.
  - `test_dados_reais.py`: leitura somente sobre `final/dados/`, incluindo a consistência entre janelas.

## Regras científicas implementadas

- Períodos: `T_i = t_{i+1} - t_i` entre mergulhos consecutivos. Ponto médio para associação de massa e janela.
- Massa no ponto médio: interpolação linear somente dentro do domínio de `massa.csv`. Fora dele, NaN e `suporte_massa = False`. Não há extrapolação, mesmo que `np.interp` a faça por padrão.
- Ajuste: `m(t) = a + b·t` por mínimos quadrados. Resíduos `observado − ajustado`. Erro padrão de `b` com `n−2` graus de liberdade.
- Taxa: só para `b < 0`, com `-b` em g/s e `-60b` em g/min. Para `b ≥ 0`, a inclinação é reportada como `inclinacao_nao_negativa`, sem taxa.
- R²: reportado como diagnóstico; não há critério baseado só nele.
- Mínimos: 3 leituras de massa para ajuste (`leituras_insuficientes` abaixo disso); 2 mergulhos para existir período; 2 períodos para desvio amostral (`sem_desvio` abaixo disso); 5 leituras recomendadas (`poucos_pontos`).

## Resultados de referência sobre os nove conjuntos reais (somente leitura)

Calculados pelas funções implementadas; ainda não gravados em disco.

| Filmagem | Ciclos | Sem suporte de massa | Período médio (s) | Desvio (s) | Taxa global (g/min) | R² global |
|---|---:|---:|---:|---:|---:|---:|
| agua_dia1 | 22 | 0 | 25,59 | 3,92 | 0,0046 | 0,242 |
| agua_dia2 | 25 | 0 | 23,20 | 4,49 | 0,0070 | 0,967 |
| agua_dia3 | 25 | 0 | 22,29 | 4,98 | 0,0063 | 0,944 |
| alcool70_dia1 | 56 | 2 | 10,61 | 3,32 | 0,0283 | 0,976 |
| alcool70_dia2 | 20 | 0 | 25,92 | 10,98 | 0,0109 | 0,666 |
| alcool70_dia3 | 36 | 1 | 16,36 | 6,48 | 0,0292 | 0,713 |
| alcool99_dia1 | 35 | 1 | 16,67 | 4,05 | 0,0444 | 0,975 |
| alcool99_dia2 | 33 | 2 | 18,16 | 5,28 | 0,0427 | 0,783 |
| alcool99_dia3 | 31 | 2 | 18,76 | 6,09 | 0,0258 | 0,670 |

Observações para interpretação (não são conclusões):

- `agua_dia1`: R² = 0,24 e resíduo máximo de 0,078 g. Resulta do salto de massa de 560 a 580 s. A inclinação da última janela é positiva, portanto não é tratada como taxa.
- Os ciclos sem suporte de massa têm ponto médio após 600 s, onde não há leitura de massa.
- Os períodos de `alcool70_dia2` têm desvio alto (10,98 s), consistente com a dúvida sobre o critério de anotação registrada em `revisao_dados_e_plano.md`.
- Os valores de referência são apenas a saída das funções sobre os dados atuais. Nenhum deles é validação científica.

## Dados

- `final/dados/`, `final/dados_old/`, `final/dados_exemplo/`, `parcial/`: não modificados. Verificados por comparação com o pacote recebido.
- Nenhum arquivo é criado em `final/resultados/`.

## Próximas etapas recomendadas

1. Prioridade 3: `pipeline.py` (orquestra uma filmagem), `graficos.py` (figuras com unidades e identificação), `relatorio.py` (CSVs e `resumo.txt`), integração em lote na CLI e gravação em `--saida`.
2. Prioridade 4: validação ponta a ponta, documentação de execução e revisão amostral das saídas.

## Limites

`parcial/` permanece histórico imutável. Dados brutos não devem ser modificados.

## Última atualização

2026-11-20. Prioridade 2 (cálculos científicos).

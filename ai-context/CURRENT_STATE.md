# Estado atual do projeto

> Estado verificado em 2026-11-20, após a Prioridade 4 (qualidade, validação ponta a ponta e documentação). Atualizar após cada execução que alterar o repositório.

## Situação geral

Prioridades 0 a 4 concluídas. A CLI valida as filmagens, processa cada uma válida isoladamente e grava as saídas em `final/resultados/<id>/`. Resultados já gerados para os nove conjuntos reais (99 arquivos). Testes de estrutura, qualidade e regressão numérica dos dados reais estão em `tests/test_dados_reais.py`. A revisão amostral de `agua_dia1` e o inventário de avisos/qualidade estão em `ai-context/REVISAO_QUALIDADE.md`.

Verificado: `python -m pytest` → 168 passed; `python -m final.analisar` sobre `final/dados/` sai com código 0; nove filmagens processadas, nenhuma falha, nenhum gráfico omitido.

## Estrutura de código

- `final/analisar.py`: CLI, descoberta, leitura e validação (Prioridade 1); integra o lote de processamento.
- `final/periodos.py`: janelas, ciclos, interpolação sem extrapolação, estatísticas e agregação por janela (Prioridade 2).
- `final/massa.py`: ajuste linear, taxas com sinal e ajustes por janela (Prioridade 2).
- `final/pipeline.py`: orquestra uma filmagem a partir do dicionário validado; não lê arquivos; recusa saída dentro dos dados (Prioridade 3).
- `final/graficos.py`: quatro figuras com unidades e identificação; `DadosInsuficientes` quando não há dados (Prioridade 3).
- `final/relatorio.py`: CSVs com precisão completa, `resumo.txt` formatado, proteção contra escrita na origem (Prioridade 3).
- `final/teste.py`: script estrutural legado, inalterado.
- `tests/`: 168 testes.
  - `test_analisar.py`: validação, lote e CLI (incluindo processamento e isolamento de falha de processamento).
  - `test_janelas.py`, `test_politicas.py`, `test_estrutura.py`.
  - `test_periodos_calculos.py`, `test_massa_calculos.py`: cálculos sintéticos.
  - `test_saidas.py`: gráficos, relatório e pipeline.
  - `test_dados_reais.py`: estrutura, qualidade, regressão numérica e ponta a ponta sobre `final/dados/` (somente leitura / saída temporária).

## Correção dos dados de massa (agua_dia1)

O pesquisador corrigiu `final/dados/agua_dia1/massa.csv` após inspeção do vídeo. Alteração verificada byte a byte:

- 28 leituras, de 20,018 s a 560,007 s, aumentaram exatamente 0,1000 g.
- As leituras de 580,007 s e 600,007 s não foram alteradas.
- Tempos inalterados. Nenhum outro arquivo mudou.

Efeito: o salto de +0,0965 g entre 560 s e 580 s desaparece e a série fica suave. O R² global sobe de 0,24 para 0,96, e o resíduo máximo cai de 0,078 g para 0,016 g. A inclinação da última janela passa de positiva para negativa. Os períodos de `agua_dia1` não mudam, porque dependem só de `mergulhadas.csv`.

Os valores de referência anteriores para `agua_dia1` (documentados na etapa 2) estavam errados por causa dessa anotação e foram substituídos abaixo.

## Resultados gerados (valores de referência)

Extraídos dos `resumo.csv` em `final/resultados/`. São saídas das funções sobre os dados atuais, não validação científica. Formalizados também como asserts de regressão em `tests/test_dados_reais.py`.

| Filmagem | Ciclos | Sem massa interpolada | Período médio (s) | Desvio (s) | Taxa global (g/min) | R² global | Resíduo máx. (g) |
|---|---:|---:|---:|---:|---:|---:|---:|
| agua_dia1 | 22 | 0 | 25,59 | 3,92 | 0,0084 | 0,964 | 0,0159 |
| agua_dia2 | 25 | 0 | 23,20 | 4,49 | 0,0070 | 0,967 | 0,0128 |
| agua_dia3 | 25 | 0 | 22,29 | 4,98 | 0,0063 | 0,944 | 0,0104 |
| alcool70_dia1 | 56 | 2 | 10,61 | 3,32 | 0,0283 | 0,976 | 0,0345 |
| alcool70_dia2 | 20 | 0 | 25,92 | 10,98 | 0,0109 | 0,666 | 0,0520 |
| alcool70_dia3 | 36 | 1 | 16,36 | 6,48 | 0,0292 | 0,713 | 0,0874 |
| alcool99_dia1 | 35 | 1 | 16,67 | 4,05 | 0,0444 | 0,975 | 0,0441 |
| alcool99_dia2 | 33 | 2 | 18,16 | 5,28 | 0,0427 | 0,783 | 0,0985 |
| alcool99_dia3 | 31 | 2 | 18,76 | 6,09 | 0,0258 | 0,670 | 0,0805 |

Observações para interpretação (não são conclusões):

- Os ciclos sem massa interpolada têm ponto médio depois de 600 s, onde não há leitura de massa.
- `alcool70_dia2` tem desvio de período de 10,98 s, consistente com a dúvida sobre o critério de anotação registrada em `REVISAO_QUALIDADE.md`.
- `alcool70_dia2`, `alcool70_dia3`, `alcool99_dia2` e `alcool99_dia3` têm resíduo máximo acima de 0,04 g e R² abaixo de 0,8; a qualidade do ajuste precisa ser lida caso a caso, junto com os resíduos.
- Nenhum gráfico foi omitido nos nove conjuntos.

## Saídas por filmagem

Em `final/resultados/<id>/`: `periodos.csv`, `massa_ajuste.csv`, `massa_residuos.csv`, `massa_por_janela.csv`, `periodo_por_janela.csv`, `resumo.csv`, `resumo.txt` e quatro PNG (`angulo_mergulhos.png`, `massa_ajuste.png`, `periodo_tempo.png`, `periodo_massa_exploratorio.png`).

## Dados

- `final/dados/` (exceto a correção de `agua_dia1/massa.csv`, feita pelo pesquisador), `final/dados_old/`, `final/dados_exemplo/`, `parcial/`: não modificados pelo software. Verificados por comparação com o pacote recebido.
- `final/resultados/`: saída derivada, gerada pela execução.

## Documentação de qualidade e limitações

- `ai-context/REVISAO_QUALIDADE.md`: inventário estrutural, avisos de validação, revisão amostral de agua_dia1, limitações experimentais.
- `resumo.txt` de cada filmagem lista avisos e limitações metodológicas.
- READMEs descrevem instalação, execução, formatos e o papel dos diretórios.

## Próximas etapas recomendadas

1. Revisão científica dos casos de baixo R² e dos desvios altos, com os gráficos de resíduos e o critério de anotação.
2. Comparação entre líquidos (água × álcool 70% × álcool 99%) em etapa própria de análise, se desejado.
3. Se necessário, refinar a documentação de limitações instrumentais após a revisão científica.

## Limites

`parcial/` permanece histórico imutável. Dados brutos não devem ser modificados pelo software.

## Última atualização

2026-11-20. Prioridade 4 (qualidade dos dados reais, validação ponta a ponta de agua_dia1, documentação e testes de regressão).

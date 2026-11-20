# Revisão de qualidade dos dados e validação ponta a ponta

Documento gerado na Prioridade 4 (2026-11-20). Não altera arquivos de dados.
Serve como registro da inspeção estrutural, dos avisos de validação e da
revisão manual amostral de uma filmagem completa.

## 1. Estrutura dos nove conjuntos reais

Todos os diretórios em `final/dados/` contêm os quatro CSVs obrigatórios e
passam pela validação de formato (`status=valida`). Resumo observado:

| Filmagem | Tracker (pts) | Massa (pts) | Mergulhos | Intervalo massa (s) | Avisos de formato |
|---|---:|---:|---:|---|---|
| agua_dia1 | 18215 | 30 | 23 | 20.018–600.007 | 1 mergulho fora do intervalo de massa (linha 2) |
| agua_dia2 | 18505 | 30 | 26 | 20.019–600.007 | 1 mergulho fora do intervalo de massa |
| agua_dia3 | 18180 | 30 | 26 | 20.019–600.007 | nenhum |
| alcool70_dia1 | 18215 | 30 | 57 | 20.027–600.015 | 4 mergulhos fora do intervalo de massa |
| alcool70_dia2 | 18084 | 30 | 21 | 20.019–600.007 | nenhum |
| alcool70_dia3 | 17824 | 30 | 37 | 20.052–600.048 | 1 mergulho fora do intervalo de massa |
| alcool99_dia1 | 18043 | 30 | 36 | 20.018–600.007 | 2 mergulhos fora do intervalo de massa |
| alcool99_dia2 | 18296 | 30 | 34 | 20.019–600.007 | 3 mergulhos fora do intervalo de massa |
| alcool99_dia3 | 17691 | 30 | 32 | 20.052–600.027 | 3 mergulhos fora do intervalo de massa |

- Massas sempre positivas e monotônicas no tempo.
- Tempos de tracker, massa e mergulhos monotônicos crescentes.
- `condicoes.csv` com uma linha e umidade em [0, 100].
- Os avisos (mergulhos fora do domínio de massa) explicam os ciclos sem
  massa interpolada reportados no resumo: o ponto médio do ciclo cai fora
  de `[primeira, última leitura de massa]`. A interpolação não extrapola.

## 2. Correção já aplicada (água_dia1)

O pesquisador corrigiu 28 leituras de `agua_dia1/massa.csv` (+0,1000 g entre
20,018 s e 560,007 s). Após a correção:

- O salto artificial de ~0,0965 g entre 560 s e 580 s desaparece.
- R² global sobe de ~0,24 para ~0,964; resíduo máximo cai para ~0,016 g.
- A inclinação da última janela passa a ser negativa (perda).
- Períodos não se alteram (dependem só de `mergulhadas.csv`).

Essa correção está refletida nos valores de referência de `CURRENT_STATE.md`
e nos testes de regressão de `tests/test_dados_reais.py`.

## 3. Validação ponta a ponta — agua_dia1

Execução: `processar_filmagem` com janela de 200 s, saída em diretório
temporário (não sobrescreve `final/resultados/`).

### 3.1 Períodos (amostras)

- 22 ciclos (= 23 mergulhos − 1).
- Primeiro ciclo: t₀ = 17,322 s → t₁ = 35,842 s; T = 18,52 s;
  ponto médio 26,582 s com massa interpolada.
- Último ciclo: t₀ = 552,520 s → t₁ = 580,273 s; T = 27,753 s;
  ponto médio 566,397 s ainda dentro do domínio de massa.
- Média amostral 25,589 s; desvio-padrão amostral 3,922 s.
- Todos os períodos positivos; nenhum ciclo sem suporte de massa.

### 3.2 Ajuste linear global da massa

- 30 leituras; status `ok`.
- \( m(t) = 41{,}6759 - 0{,}00013920\,t \) (g, t em s).
- Taxa positiva de perda: 0,00013920 g/s ≡ 0,008352 g/min.
- R² = 0,96396; resíduo máximo absoluto = 0,01592 g;
  erro padrão de b ≈ 5,09×10⁻⁶ g/s.
- Diagnósticos: nenhum.

### 3.3 Janelas de 200 s

| Janela | Intervalo (s) | Leituras | n ciclos | Taxa (g/min) | R² local |
|---|---|---:|---:|---:|---:|
| 1 | [0, 200) | 9 | 8 | 0,0115 | 0,75 |
| 2 | [200, 400) | 10 | 8 | 0,0086 | 0,76 |
| 3 | [400, 600,007] | 11 | 6 | 0,0074 | 0,996 |

A última janela absorve o resto do ensaio, conforme a convenção de
`periodos.py`. Todos os pontos de massa e ciclos no domínio são contabilizados.

### 3.4 Saídas geradas

Arquivos presentes e não vazios: `periodos.csv`, `massa_ajuste.csv`,
`massa_residuos.csv`, `massa_por_janela.csv`, `periodo_por_janela.csv`,
`resumo.csv`, `resumo.txt`, e os quatro PNG. O `resumo.txt` lista o aviso
de validação e as limitações metodológicas.

### 3.5 Conclusão da amostra

Os números batem com o cálculo direto (construção de ciclos + `polyfit`
equivalente) e com a tabela de referência. Nenhuma evidência de
corrupção, extrapolação indevida ou perda de pontos na agregação por janela.

## 4. Observações de qualidade para interpretação (não são erros de software)

- **Ciclos sem massa interpolada**: ocorrem quando o ponto médio cai após
  a última leitura de massa (~600 s). São reportados explicitamente;
  a massa fica `NaN` e não entra em estatísticas que dependem dela.
- **R² baixo / resíduo alto**: `alcool70_dia2` (R²≈0,67, resid≈0,052 g),
  `alcool70_dia3`, `alcool99_dia2` e `alcool99_dia3` merecem leitura
  conjunta dos gráficos de resíduos e do critério de anotação dos
  mergulhos. O software não descarta pontos automaticamente.
- **Desvio de período elevado** em `alcool70_dia2` (~11 s) é consistente
  com possível variação no critério de marcação manual.
- **Movimento do pássaro na balança**: pode introduzir oscilações de massa
  de curto prazo; o ajuste linear global e os resíduos são o diagnóstico,
  não uma correção silenciosa.
- Condições ambientais são um único registro por filmagem; não há série
  temporal de temperatura/umidade.

Esses pontos são limitações experimentais e de anotação, documentadas para
o pesquisador. A validação de formato e o pipeline não os mascaram.

## 5. Proteção dos dados

- Nenhuma escrita em `final/dados/`, `final/dados_exemplo/`,
  `final/dados_old/` ou `parcial/`.
- Resultados derivados vão para diretório de saída configurável
  (padrão `final/resultados/`).
- Testes de regressão e de processamento usam `tmp_path` ou somente leitura.

## 6. Testes que formalizam esta revisão

- `tests/test_dados_reais.py`:
  - estrutura e monotonia dos nove conjuntos;
  - contagem de ciclos sem suporte de massa;
  - regressão numérica contra a tabela de referência;
  - processamento completo em diretório temporário;
  - amostra ponta a ponta de `agua_dia1` (primeiro/último ciclo, resumo).

Execução: `python -m pytest tests/test_dados_reais.py`.

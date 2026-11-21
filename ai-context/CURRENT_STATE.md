# Estado atual do projeto

> Estado verificado em 2026-11-20, após a etapa 4 (calor latente NIST, L·r com incerteza, comparação dia a dia). Atualizar após cada execução que alterar o repositório.

## Situação geral

Prioridades 0–4 concluídas (ver `TASKS.md`), e a etapa 4 implementada. O pipeline valida, processa e grava por filmagem; a CLI gera também a comparação entre filmagens. Os resultados oficiais estão em `final/resultados/` (112 arquivos: 9 filmagens × 10 arquivos, e 22 arquivos de comparação).

Verificado: `python -m final.analisar` sobre `final/dados/` sai com código 0; nove filmagens processadas, nenhuma falha; suíte de 210 testes passando; versões mínimas declaradas (numpy 1.26, pandas 2.1, matplotlib 3.8, scipy 1.11, pytest 7.4) passando em Python 3.10, 3.11 e 3.12.

## Decisões de análise em vigor (2026-11-20)

- **Comparação principal dia a dia:** em cada dia, os três líquidos (um pássaro cada) com as condições do próprio dia. Variação entre dias reportada à parte.
- **Líquidos:** `agua`; `alcool 70%` = etanol **70 % em massa (w/w)**; `alcool 99%` = **isopropanol**.
- **Calor latente:** NIST (ΔvapH/M). Mistura 70 %: primário pela fração mássica do **vapor** (Raoult ideal, composição inicial); alternativo pela fração do líquido, como sensibilidade. Pressão do isopropanol a 25 °C é extrapolação de Antoine.
- **Grandeza comparada com o período:** L·r (W), com r = −b. IC95% por propagação de primeira ordem.
- **Corrida piloto** do relatório parcial excluída.
- **Mergulhos:** anotação manual, sem alteração. Critério formal adiado.
- **Hipóteses:** ordenações (H2; τ ∝ 1/(L·r)) são descritivas, com n = 3 por dia. Nenhuma validada ou refutada.

## Estrutura de código

- `final/analisar.py`: CLI, descoberta, leitura e validação (inclui validação do nome do líquido); integra o processamento e a comparação.
- `final/pipeline.py`: orquestra uma filmagem; calcula taxa com IC, L, L·r com IC, períodos com IC; grava tabelas, resumo e gráficos.
- `final/periodos.py`: janelas, ciclos, interpolação sem extrapolação, estatísticas com IC95% da média (t).
- `final/massa.py`: ajuste linear, IC95% de b e da taxa, ajustes por janela.
- `final/constantes.py` (**novo**): propriedades NIST, pressão de vapor, L da mistura, quantil t, L·r. Justificativa: propriedades físicas com fonte, separadas dos cálculos de ajuste.
- `final/comparacao.py` (**novo**): comparação dia a dia e entre dias. Justificativa: não pertence a nenhuma filmagem isolada.
- `final/graficos.py`: figuras por filmagem e de comparação; formatação numérica fixa.
- `final/relatorio.py`: CSV com precisão completa; resumo em texto com formatos fixos.
- `final/teste.py`: script estrutural legado, inalterado.
- `tests/`: 210 testes. Incluem `test_constantes_incertezas.py` (valores à mão e por scipy), `test_comparacao.py` (filmagens processadas reais, sintéticas), `test_referencia_etapa4.py` (referência independente sobre os dados reais: taxa, IC e L·r de cada filmagem).

## Verificações desta etapa

- **Referência independente:** taxa, IC95% e L·r das nove filmagens recalculados só com numpy/scipy a partir dos CSVs, com L escrito à mão a partir do NIST; coincidem com o pipeline (rel. 1e-9). Durante a verificação, um erro de sinal na minha referência (pressão da água) foi detectado e corrigido.
- **Mutações:** L primário trocado pelo alternativo (detectado); quantil normal no lugar do t (detectado, 3 testes); limites do IC da taxa invertidos (detectado, 14 testes).
- **Versões mínimas:** suíte completa passa com numpy 1.26.4, pandas 2.1.4, matplotlib 3.8.4, scipy 1.11.4 e pytest 7.4.4 em Python 3.10.20, 3.11.15 e 3.12.3.
- **Figuras:** inspeção visual das figuras de massa (rótulo da taxa), τ × L·r (escala log) e entre dias.

## Valores de referência (saídas do pipeline, nove filmagens)

Extraídos dos `resumo.csv` gerados. IC95% entre colchetes. Saídas das funções sobre os dados atuais, não validação científica.

| Filmagem | Líquido | Dia | T (°C) | UR (%) | Ciclos | τ médio (s) [IC95%] | Taxa (g/min) [IC95%] | L (kJ/kg) | L·r (W) [IC95%] |
|---|---|---|---:|---:|---:|---|---|---:|---|
| agua_dia1 | agua | 2026-10-19 | 23.4 | 53 | 22 | 25.59 [23.85, 27.33] | 0.0084 [0.0077, 0.0090] | 2442.4 | 0.3400 [0.3145, 0.3654] |
| agua_dia2 | agua | 2026-10-26 | 23.9 | 64 | 25 | 23.20 [21.34, 25.05] | 0.0070 [0.0065, 0.0075] | 2442.4 | 0.2832 [0.2630, 0.3033] |
| agua_dia3 | agua | 2026-11-09 | 23.9 | 60 | 25 | 22.29 [20.23, 24.34] | 0.0071 [0.0066, 0.0075] | 2442.4 | 0.2875 [0.2693, 0.3056] |
| alcool70_dia1 | alcool 70% | 2026-10-19 | 23.0 | 60 | 35 | 16.97 [14.71, 19.23] | 0.0283 [0.0266, 0.0300] | 1142.4 | 0.5380 [0.5051, 0.5708] |
| alcool70_dia2 | alcool 70% | 2026-10-26 | 23.9 | 64 | 20 | 25.92 [21.53, 30.32] | 0.0207 [0.0191, 0.0223] | 1142.4 | 0.3941 [0.3643, 0.4239] |
| alcool70_dia3 | alcool 70% | 2026-11-09 | 23.9 | 61 | 28 | 21.03 [17.93, 24.13] | 0.0312 [0.0291, 0.0333] | 1142.4 | 0.5939 [0.5533, 0.6346] |
| alcool99_dia1 | alcool 99% | 2026-10-19 | 23.0 | 60 | 35 | 16.67 [15.28, 18.06] | 0.0355 [0.0337, 0.0374] | 748.8 | 0.4433 [0.4057, 0.4808] |
| alcool99_dia2 | alcool 99% | 2026-10-26 | 23.9 | 64 | 33 | 18.16 [16.29, 20.03] | 0.0318 [0.0303, 0.0332] | 748.8 | 0.3966 [0.3644, 0.4288] |
| alcool99_dia3 | alcool 99% | 2026-11-09 | 23.9 | 61 | 31 | 18.76 [16.52, 20.99] | 0.0288 [0.0274, 0.0303] | 748.8 | 0.3600 [0.3302, 0.3898] |

Temperatura e umidade são as de `condicoes.csv`. Umidade varia de 53 % a 64 % entre dias; a diferença de 11 pontos no dia 1 da água excede a incerteza de ±5 % do aparelho.

**Descritivo por dia** (`comparacao/por_dia/*/hipoteses_dia.csv`):

- 2026-10-19: ordem de τ = álcool 99% < álcool 70% < água (coincide com H2). Ordem prevista por L·r não coincide. Inclinação log–log = −0,94.
- 2026-10-26: ordem de τ = álcool 99% < água < álcool 70% (não coincide com H2). Ordem prevista por L·r não coincide. Inclinação = −0,22.
- 2026-11-09: ordem de τ = álcool 99% < álcool 70% < água (coincide com H2). Ordem prevista por L·r não coincide. Inclinação = −0,03.

Observações (descritivas, sem conclusão):

- O isopropanol tem o menor τ nos três dias.
- A ordem prevista por L·r não coincide em nenhum dia. Com L primário (1142 kJ/kg) para a mistura, o álcool 70 % tem o maior L·r em dois dos três dias, o que o colocaria como o de menor período.
- O efeito de ambiente é grande: o período do álcool 70 % varia de 16,97 s a 25,92 s entre dias. Comparações entre dias são confundidas com ambiente e com o pássaro.
- Com n = 3 por dia, as inclinações log–log são descritivas.

## Dados

- `final/dados/`, `final/dados_old/`, `final/dados_exemplo/`, `parcial/`: não alterados pelo software.
- `final/resultados/`: saída derivada, gerada pela execução.

## Limitações declaradas

- Um pássaro por líquido: efeito de líquido e de pássaro confundidos (ver EXPERIMENT.md).
- Composição da mistura 70 % muda com o tempo (etanol evapora primeiro); L primário usa a composição inicial.
- Pressão de vapor do isopropanol a 25 °C é extrapolação.
- Dependência de L com a temperatura não é corrigida (ver `constantes.py`).
- Critério de mergulho manual, não formalizado; bolhas sem mergulho podem gerar intervalos irregulares.
- Propagação de incerteza de primeira ordem; a mistura não entra no IC.
- Usar `float_precision="round_trip"` ao ler os CSVs.

## Próximas etapas (não executadas)

1. Formalizar o critério de mergulho e a categoria "meia-mergulhada", com segundo anotador e concordância.
2. Decidir a análise principal (dia a dia com agregação, ou global com dia como fator).
3. Sensibilidade: L alternativo da mistura, janelas de 100/200/300 s, critério de mergulho.
4. Redação do relatório (fora do escopo do software).

## Última atualização

2026-11-20. Etapa 4: constantes NIST, L·r com incerteza, comparação dia a dia e entre dias.

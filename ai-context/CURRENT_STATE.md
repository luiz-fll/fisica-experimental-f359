# Estado atual do projeto

> Estado verificado em 2026-11-20, após a etapa de fundação (Prioridade 0 de `TASKS.md`). Atualizar após cada execução que alterar o repositório.

## Situação geral

Fundação (Prioridade 0) e entrada/validação (Prioridade 1) concluídas. A CLI valida as filmagens, identifica erros e avisos por arquivo e linha, e isola falhas no lote. Ainda não há cálculos científicos: períodos, interpolação, ajustes de massa, gráficos, gravação de resultados e pipeline são as próximas etapas.

Verificado: `python -m final.analisar` sobre `final/dados/` sai com código 0; as nove filmagens são válidas, sem erros nem avisos.

## Estrutura de código

- `final/analisar.py`: **implementado** — CLI (`--diretorio`, `--saida`, `--janela`), `descobrir_filmagens`, `carregar_filmagem`, `validar_lote`, `Problema`, `ErroFilmagem`. Lê e valida; não calcula. Não grava arquivos.
- `final/periodos.py`: **parcialmente implementado** — `definir_limites_janelas`, `atribuir_janela` (testadas). Demais funções: contrato (`NotImplementedError`).
- `final/massa.py`: constantes de mínimo de leituras. `ajustar_linear`, `taxa_de_perda`, `ajustar_janelas`: contrato.
- `final/pipeline.py`, `final/graficos.py`, `final/relatorio.py`: contratos documentados.
- `final/teste.py`: script estrutural legado, inalterado.
- `tests/`: 85 testes, em `test_analisar.py` (filmagens sintéticas: cada regra de erro e aviso, leitura sem modificação, BOM/CRLF, isolamento, CLI e códigos de saída), `test_janelas.py`, `test_politicas.py`, `test_estrutura.py` e `test_dados_reais.py` (somente leitura sobre `final/dados/`).

Verificações de mutação: remover a checagem de duplicatas e remover o isolamento do lote, ambas, fazem testes falharem.

## Validação dos dados (estado atual)

- `final/dados/`: 9 válidas, 0 erros, 0 avisos.
- `final/dados_old/`: 4 inválidas (`agua_dia3`, `alcool70_dia3`, `alcool99_dia1`, `alcool99_dia3`) e avisos de divergência de ângulo em `alcool70_dia1`. Consistente com os problemas já registrados nessa cópia antiga.
- `final/dados_exemplo/`: válida, mas com tracker de apenas 0–0,067 s; mergulhos fora do intervalo do tracker. Não serve como amostra analítica.

## Dados

- `final/dados/`, `final/dados_old/`, `final/dados_exemplo/`, `parcial/`: não modificados. Verificados por comparação com o pacote recebido.
- Nenhum arquivo é criado em `final/resultados/` nesta etapa.

## Próximas etapas recomendadas

1. Prioridade 2: `periodos.py` (ciclos, interpolação no ponto médio sem extrapolação, estatísticas globais e por janela) e `massa.py` (ajuste global, resíduos, taxas, ajustes locais), com testes sintéticos.
2. Prioridade 3: `pipeline.py`, `graficos.py`, `relatorio.py` e gravação dos resultados em `--saida`.
3. Prioridade 4: testes de casos-limite restantes, validação ponta a ponta e documentação final de execução.

## Limites

`parcial/` permanece histórico imutável. Dados brutos não devem ser modificados.

## Última atualização

2026-11-20. Prioridade 1 (entrada e validação).

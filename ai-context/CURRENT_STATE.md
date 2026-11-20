# Estado atual do projeto

> Estado verificado em 2026-11-20, após a etapa de fundação (Prioridade 0 de `TASKS.md`). Atualizar após cada execução que alterar o repositório.

## Situação geral

A fundação está concluída: dependências declaradas, suíte de testes configurada, contratos das funções dos seis módulos definidos e a convenção de janelas temporais implementada e testada. A análise ainda não é executável: a CLI (`final/analisar.py`) retorna código 2 com aviso, e as demais funções de cálculo, gráficos e relatórios têm apenas contratos (`NotImplementedError`).

## Dependências e execução de testes

- `requirements.txt`: `numpy>=1.24`, `pandas>=2.0`, `matplotlib>=3.7`. Python 3.10+ declarado.
- `requirements-dev.txt`: inclui `requirements.txt` e `pytest>=7.0`.
- `pytest.ini`: `testpaths = tests`, `pythonpath = final`.
- Verificado: Python 3.12.3, numpy 2.5.4, pandas 3.0.6, matplotlib 3.11.2, pytest 9.2.0.
- Não verificado: os limites inferiores das bibliotecas e Python 3.10 e 3.11.

## Estrutura de código

- `final/periodos.py`: **implementado** — `definir_limites_janelas`, `atribuir_janela`, constantes de origem, duração e mínimos. Demais funções (`construir_ciclos`, `interpolar_massa`, `estatisticas_periodos`, `periodos_por_janela`): contrato, `NotImplementedError`.
- `final/massa.py`: constantes de mínimo de leituras (`MIN_LEITURAS_AJUSTE = 3`, `LEITURAS_RECOMENDADAS_AJUSTE = 5`). `ajustar_linear`, `taxa_de_perda`, `ajustar_janelas`: contrato.
- `final/analisar.py`: `ErroFilmagem` implementada; `main` retorna código 2 com aviso. `descobrir_filmagens` e `carregar_filmagem`: contrato.
- `final/pipeline.py`, `final/graficos.py`, `final/relatorio.py`: contratos documentados.
- `final/teste.py`: script estrutural legado, inalterado.
- `tests/`: `test_janelas.py` (fronteiras, absorção da última janela, tolerância numérica, entradas inválidas, instantes fora do domínio), `test_politicas.py` (constantes documentadas), `test_estrutura.py` (importação dos seis módulos). **35 testes passando.**
- Imports: `from final.<modulo> import ...`. Execução: `python -m final.analisar`.

## Convenção de janelas (implementada)

- Origem em 0 s; janelas `[início, fim)` de `L = 200 s` (padrão); a última absorve o resto do ensaio, `[(N-1)·L, t_fim]`, fechada à direita.
- `N = max(1, floor(t_fim / L))`, com tolerância numérica que não cria janela começando após `t_fim`.
- Verificação de mutação: reverter a absorção da última janela faz 5 testes falharem.
- Com os nove conjuntos reais: 3 janelas por filmagem, com 9, 10 e 11 leituras de massa; nenhuma observação sem janela.

## Dados

- `final/dados/`: nove filmagens reais (água, álcool 70% e álcool 99%, três dias cada), com os quatro CSVs e o `.trk`. Não modificados nesta etapa.
- `final/dados_exemplo/`, `final/dados_old/`, `parcial/` e `final/resultados/`: verificados como idênticos ao pacote recebido.
- Os problemas de qualidade dos dados estão registrados em `revisao_dados_e_plano.md` e não são corrigidos automaticamente.

## Próximas etapas recomendadas

1. Prioridade 1: `analisar.py` — descoberta, leitura e validação dos quatro CSVs, com `ErroFilmagem` e continuidade do lote.
2. Prioridade 2: `periodos.py` (ciclos, interpolação, estatísticas) e `massa.py` (ajustes), com testes sintéticos.
3. Prioridades 3 e 4: pipeline, gráficos, relatórios, CLI em lote e validação ponta a ponta.

## Limites

`parcial/` permanece histórico imutável. Dados brutos em `final/dados/`, `final/dados_exemplo/` e `final/dados_old/` não devem ser modificados.

## Última atualização

2026-11-20. Fundação (Prioridade 0), com última janela absorvendo o resto e imports `final.<modulo>`. Nenhuma função científica foi implementada além das janelas temporais.

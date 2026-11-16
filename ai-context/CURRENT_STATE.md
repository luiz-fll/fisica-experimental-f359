# Estado atual do projeto

> Documento-base inicializado para preparar o repositório para desenvolvimento agêntico. Deve ser reescrito ao final de cada execução de trabalho.

## Situação geral
O repositório contém registros do trabalho exploratório do relatório parcial em `parcial/` e uma área destinada à implementação final em `final/`. A implementação final será refeita conforme `ai-context/PROJECT.md`; os scripts exploratórios não serão reaproveitados automaticamente.

## Implementação final
- A arquitetura-alvo possui seis módulos: `analisar.py`, `pipeline.py`, `periodos.py`, `massa.py`, `graficos.py` e `relatorio.py`.
- Os módulos estavam vazios na versão do repositório inspecionada para preparar este contexto.
- A especificação de entradas, métodos e saídas está em `ai-context/PROJECT.md`.

## Dados
- O formato-alvo de cada filmagem exige `tracker.csv`, `massa.csv`, `mergulhadas.csv` e `condicoes.csv`.
- Na versão inspecionada, `final/dados/` continha pastas de filmagem com arquivos do Tracker e exportações `tracker.csv`, mas não foi constatada a presença dos outros três CSVs obrigatórios em cada pasta.
- `final/dados_exemplo/filmagem_exemplo/` contém exemplos dos quatro CSVs e serve como referência estrutural, não como validação científica de dados reais.

## Área histórica
- `parcial/` contém scripts, CSVs, imagens e resultados usados na análise exploratória e no relatório parcial.
- Esta pasta é somente histórica e está protegida contra alterações pelo `AGENTS.md`.

## Testes
- Não há suíte de testes da implementação final estabelecida neste estado inicial.
- Testes devem ser criados junto com os módulos e cálculos.

## Próximos passos recomendados
1. Confirmar a localização final dos módulos (raiz do repositório, conforme decisão registrada).
2. Definir contratos das funções e política de janelas.
3. Implementar leitura e validação de entradas.
4. Implementar e testar `periodos.py` e `massa.py` antes de gráficos e relatórios.
5. Completar uma filmagem real com os quatro CSVs para validação ponta a ponta.

## Última atualização
Preparação inicial dos arquivos de contexto. A IA deve substituir este estado quando realizar a primeira tarefa técnica.

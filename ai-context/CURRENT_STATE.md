# Estado atual do projeto

> Estado verificado na revisão do pacote `fisica-experimental-f359-main` recebido em 2026-11-20. Atualizar após cada execução que alterar o repositório.

## Situação geral

O repositório contém a documentação de contexto em `ai-context/` e a área de implementação/dados em `final/`. A implementação final ainda não está desenvolvida: os seis módulos planejados estão presentes, mas vazios. O único script Python não vazio em `final/` é `teste.py`, um reconhecedor estrutural de diretórios que imprime os nomes das filmagens e parâmetros; ele não lê CSVs nem realiza análise.

## Estrutura observada

- `final/analisar.py`, `pipeline.py`, `periodos.py`, `massa.py`, `graficos.py`, `relatorio.py`: arquivos existentes, todos com zero bytes.
- `final/teste.py`: script estrutural de demonstração; não é teste automatizado nem CLI de análise.
- `final/dados/`: nove filmagens reais, organizadas em três condições nominais e três dias por condição.
- `final/dados_exemplo/filmagem_exemplo/`: um conjunto reduzido com os quatro CSVs.
- `final/dados_old/`: cópia anterior dos CSVs das nove filmagens; não usar como entrada padrão nem confundir com a versão atual.
- `final/`: contém arquivos `.trk` para as filmagens reais e para o exemplo.
- Não foi encontrada pasta `tests/`, arquivo de dependências (`requirements.txt`/`pyproject.toml`) ou configuração de testes no pacote inspecionado.

## Dados atuais

As nove pastas em `final/dados/` contêm os quatro CSVs esperados. Cada `condicoes.csv` tem uma linha. Contagens observadas:

| Filmagem | tracker.csv | massa.csv | mergulhadas.csv |
|---|---:|---:|---:|
| agua_dia1 | 18.215 | 30 | 23 |
| agua_dia2 | 18.505 | 30 | 26 |
| agua_dia3 | 18.180 | 30 | 26 |
| alcool70_dia1 | 18.215 | 30 | 57 |
| alcool70_dia2 | 18.084 | 30 | 21 |
| alcool70_dia3 | 17.824 | 30 | 37 |
| alcool99_dia1 | 18.043 | 30 | 36 |
| alcool99_dia2 | 18.296 | 30 | 34 |
| alcool99_dia3 | 17.691 | 30 | 32 |

Os cabeçalhos reais diferem dos exemplos da documentação anterior:
- `tracker.csv`: `tempo_seg,angulo_deg`.
- `massa.csv`: `tempo_seg,massa_g`.
- `mergulhadas.csv`: `tempo_seg,angulo_deg` (não há `evento_id`).
- `condicoes.csv`: `liquido,dia,temperatura_c,umidade_pct` (sufixo `c` minúsculo).

O exemplo em `final/dados_exemplo/filmagem_exemplo/` também usa `tempo_seg` e `temperatura_c`; seu `mergulhadas.csv` contém `tempo_seg,angulo_deg`. A documentação foi alinhada a esses cabeçalhos observados. As contagens acima são inventário, não validação científica nem garantia de ausência de problemas internos nos dados.

## Estado de implementação

- CLI de análise: não implementada.
- Descoberta, leitura e validação de CSVs: não implementadas.
- Cálculo de períodos/interpolação: não implementado.
- Ajustes globais/locais de massa: não implementados.
- Geração de gráficos e relatórios: não implementada.
- Testes automatizados: inexistentes no pacote inspecionado.
- Execução ponta a ponta: não disponível.

## Próximas etapas recomendadas

1. Definir dependências e versão mínima de Python; criar ambiente e testes.
2. Fechar os contratos de dados/funções entre módulos.
3. Implementar leitura/validação compatível com os cabeçalhos reais sem editar os CSVs.
4. Implementar e testar períodos/interpolação e ajustes de massa com dados sintéticos.
5. Integrar pipeline, gráficos, relatórios e CLI.
6. Executar validação ponta a ponta em filmagens reais, registrando limitações e resultados.

## Limites

`parcial/` permanece histórico imutável e fora do escopo de inspeção/alteração, salvo solicitação histórica explícita. Dados brutos em `final/dados/`, `final/dados_exemplo/` e `final/dados_old/` não devem ser modificados.

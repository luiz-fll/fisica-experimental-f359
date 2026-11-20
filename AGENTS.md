# Instruções para agentes de IA

## Missão e fonte de verdade

Manter e desenvolver o pipeline reprodutível de análise do experimento do pássaro bebedor. Trabalhe a partir do repositório presente, não de estados descritos em handoffs antigos.

Antes de qualquer alteração:
1. Leia este arquivo.
2. Leia `ai-context/CURRENT_STATE.md` e `ai-context/TASKS.md`.
3. Consulte `ai-context/PROJECT.md` para os contratos técnicos e `ai-context/EXPERIMENT.md` para o contexto físico.
4. Consulte `ai-context/HANDOFF.md` quando relevante.
5. Inspecione os arquivos de código, dados e testes diretamente relacionados à tarefa.

Não leia todo `ai-context/LOG.md` por padrão; consulte-o apenas quando precisar da origem de uma decisão. O código e os dados atuais são evidência do estado implementado; documentos de planejamento não provam que algo foi implementado.

## Limites de escopo — obrigatórios

- **Nunca editar, mover, renomear, apagar, reorganizar ou integrar `parcial/`.**
- `parcial/` é registro histórico do relatório parcial. Não consultar seu conteúdo, exceto quando o usuário pedir explicitamente comparação ou esclarecimento histórico.
- Não copiar scripts, tabelas, resultados ou figuras de `parcial/` para a implementação final.
- Não alterar os dados experimentais em `final/dados/`, `final/dados_exemplo/` ou `final/dados_old/`. São entradas/registros, não área de trabalho.
- Não sobrescrever arquivos `.trk` nem CSVs originais. Resultados derivados devem ser gravados em diretório separado.
- Não apagar arquivos ou resultados sem autorização explícita.
- Alterar apenas arquivos necessários à tarefa solicitada. Se o pedido restringir os tipos de arquivo, respeite a restrição estritamente.

## Arquitetura e organização vigentes

A implementação final está localizada em `final/`, não na raiz do repositório. Os módulos planejados são:
- `final/analisar.py`: CLI, descoberta, leitura e validação das filmagens.
- `final/pipeline.py`: orquestração de uma filmagem.
- `final/periodos.py`: ciclos, períodos, interpolação de massa e estatísticas.
- `final/massa.py`: ajustes globais/locais e diagnósticos da massa.
- `final/graficos.py`: visualizações a partir de resultados calculados.
- `final/relatorio.py`: exportação de tabelas e resumos.

Não mover esses arquivos para a raiz sem decisão explícita do usuário. Não criar módulos extras sem necessidade demonstrada e justificativa. `final/teste.py` é um script estrutural legado e não substitui `analisar.py` nem uma suíte automatizada.

## Integridade científica

- Não invente, complete ou estime silenciosamente observações ausentes.
- Diferencie medição, cálculo, interpolação, ajuste, hipótese e interpretação.
- Não descarte pontos por parecerem discrepantes sem critério declarado e autorização metodológica. O movimento do pássaro pode afetar a balança; isso é limitação a diagnosticar, não justificativa automática para remover dados.
- Não escolha janelas após observar os resultados para forçar linearidade. A duração deve ser definida antes e configurável.
- Não use R² isoladamente como prova de adequação do modelo; examine resíduos, quantidade e distribuição temporal dos pontos e limitações instrumentais.
- Não conclua que uma hipótese foi validada apenas porque a ordenação observada coincide com a previsão.
- Preserve unidades em nomes de colunas, eixos, relatórios e documentação.
- Não trate aproximações físicas como leis universais.

## Dados e convenções observadas

Cada subdiretório direto de `final/dados/` representa uma filmagem independente. Os nomes atuais identificam os ensaios, mas o programa deve tratá-los como identificadores opacos; metadados vêm de `condicoes.csv`.

Cabeçalhos observados nesta versão:
- `tracker.csv`: `tempo_seg,angulo_deg`.
- `massa.csv`: `tempo_seg,massa_g`.
- `mergulhadas.csv`: `tempo_seg,angulo_deg`. Cada linha marca um mergulho selecionado manualmente; não há coluna `evento_id` neste conjunto.
- `condicoes.csv`: `liquido,dia,temperatura_c,umidade_pct`, com uma linha por filmagem.

Não renomear cabeçalhos ou alterar CSVs para fazê-los coincidir com uma especificação antiga. O código deve aceitar o formato presente ou uma migração deve ser aprovada e documentada sem modificar os originais.

## Engenharia e testes

- Use caminhos relativos ao projeto e `pathlib`; evite caminhos absolutos e estado global.
- Mantenha funções pequenas, contratos explícitos e dependências justificadas.
- Leia cada CSV uma única vez por filmagem e passe os dados carregados explicitamente ao pipeline.
- Não misture observações de filmagens diferentes em cálculos individuais.
- Valide dados e apresente erros acionáveis, identificando filmagem e arquivo.
- Após alterações de código, execute testes relevantes e acrescente testes para novos casos. Verifique dados vazios, poucos pontos, duplicatas, valores não numéricos, eventos fora do intervalo e janelas insuficientes.
- Se não puder executar testes, declare exatamente o que ficou sem verificação. Nunca afirme funcionamento sem evidência.

## Atualização da documentação agêntica

Ao concluir uma tarefa técnica:
1. Atualize `ai-context/TASKS.md` de acordo com o que foi realmente concluído.
2. Reescreva `ai-context/CURRENT_STATE.md` com o estado verificado.
3. Acrescente uma entrada concisa ao final de `ai-context/LOG.md`; é append-only.
4. Atualize `ai-context/HANDOFF.md` apenas se decisões ou contexto de continuidade mudarem significativamente.
5. Atualize `PROJECT.md` somente quando contratos/requisitos mudarem; mantenha-o alinhado ao formato real dos dados.
6. Atualize README(s) quando instruções ou estrutura para usuários mudarem.

## Comunicação

Na resposta final, resuma as alterações, liste arquivos relevantes, informe verificações executadas e limitações. Não oculte pendências nem confunda planejamento com implementação.

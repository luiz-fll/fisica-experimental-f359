# Instruções para agentes de IA

## 1. Missão
Desenvolver e manter o software de análise de dados do experimento do pássaro bebedor, seguindo a arquitetura, os critérios científicos e os contratos documentados em `ai-context/`.

## 2. Leitura de contexto
Antes de alterar código:
1. Leia este arquivo.
2. Leia `ai-context/CURRENT_STATE.md` e `ai-context/TASKS.md`.
3. Consulte `ai-context/PROJECT.md` para requisitos de software.
4. Consulte `ai-context/EXPERIMENT.md` para significado físico e metodologia.
5. Leia `ai-context/HANDOFF.md` quando houver instruções de transferência relevantes.
6. Consulte o código e os testes existentes; os documentos não substituem a inspeção do repositório.

Não leia todo `ai-context/LOG.md` por padrão. Consulte-o apenas se precisar investigar a origem de uma decisão ou alteração.

## 3. Limites de escopo — regra crítica
- **Nunca editar, mover, renomear, apagar ou reorganizar `parcial/`.**
- `parcial/` é um registro histórico do trabalho exploratório utilizado no relatório parcial. Não é código-base para o relatório final e não deve ser refatorado, corrigido nem integrado.
- Não copiar automaticamente scripts ou resultados de `parcial/` para a implementação final. É permitido consultá-los apenas quando o usuário pedir explicitamente uma comparação ou esclarecimento histórico.
- A implementação final deve ser refeita de acordo com `PROJECT.md` e a arquitetura atual.
- Não alterar dados experimentais brutos em `final/dados/` (ou na pasta de dados definida pelo usuário). Não sobrescrever arquivos originais.
- Não apagar arquivos, resultados ou dados sem autorização explícita.
- Não modificar arquivos fora do escopo da tarefa.

## 4. Regras científicas e de integridade
- Não invente, complete ou estime silenciosamente observações experimentais ausentes.
- Preserve os valores brutos. Transformações devem gerar novos resultados derivados, nunca substituir os dados originais.
- Diferencie claramente medição, cálculo, interpolação, ajuste, hipótese e interpretação.
- Não descarte pontos por parecerem discrepantes sem critério declarado e autorização metodológica. A movimentação do pássaro pode afetar a balança; isso é uma limitação experimental a analisar, não justificativa automática para remover dados.
- Não force linearidade escolhendo intervalos após olhar os resultados. O tamanho da janela é definido previamente e configurável.
- Não apresente R² isoladamente como prova de adequação do modelo. Examine resíduos, quantidade e distribuição temporal dos pontos e limitações instrumentais.
- Não conclua que uma hipótese foi validada apenas porque a ordem observada coincide com a previsão. Considere dispersão, condições ambientais, pássaros distintos e limitações do modelo.
- Registre unidades em nomes de colunas, eixos, relatórios e documentação.
- Não transforme hipóteses físicas simplificadas em leis universais.

## 5. Regras de engenharia
- Siga a arquitetura modular definida em `ai-context/PROJECT.md`.
- Mantenha funções pequenas, com entradas e saídas explícitas.
- Evite estado global, caminhos absolutos e dependências ocultas entre módulos.
- Não duplique leitura de CSV nem cálculos científicos em módulos de apresentação.
- Use `pathlib` para caminhos e `pandas`/`numpy`/`matplotlib`/`scipy` somente quando forem dependências justificadas pelo projeto.
- Valide entradas e apresente mensagens de erro acionáveis.
- Uma filmagem deve ser processada isoladamente. Nunca concatenar filmagens para calcular ajuste, períodos ou estatísticas individuais.
- Não assuma intervalo constante entre leituras de massa; use os tempos registrados.
- Não assuma que os nomes das pastas têm semântica fixa. O nome identifica a filmagem e deve ser preservado na saída.
- Preserve compatibilidade com os formatos documentados ou atualize a especificação e os exemplos junto com uma mudança aprovada.

## 6. Testes e verificações
Após alterações:
- Execute os testes relevantes.
- Acrescente testes para novos cálculos, casos-limite e validação de entradas.
- Verifique especialmente dados vazios, poucos pontos, tempos duplicados, valores não numéricos, eventos fora do intervalo e janelas com poucos ciclos.
- Se não puder executar testes, informe exatamente o que não foi verificado e por quê.
- Não afirme que algo funciona sem teste ou evidência.

## 7. Atualização de contexto ao terminar
Ao concluir uma tarefa:
1. Atualize `ai-context/TASKS.md` se o estado das tarefas mudou.
2. Reescreva `ai-context/CURRENT_STATE.md` para refletir o estado real após a execução.
3. Acrescente uma entrada concisa ao final de `ai-context/LOG.md`; não reescreva o histórico.
4. Atualize `ai-context/HANDOFF.md` somente se houver contexto específico importante para a próxima sessão, tarefa interrompida ou transferência entre agentes.
5. Não altere `EXPERIMENT.md` ou `PROJECT.md` apenas para refletir a implementação. Esses arquivos são referências; atualize-os somente quando requisitos ou conhecimento documentado mudarem.

O log é append-only. Não é necessário ler o log inteiro para acrescentar uma entrada. Não invente data, testes, decisões ou alterações.

## 8. Comunicação
Na resposta final:
- Resuma o que foi alterado.
- Liste arquivos relevantes.
- Informe testes executados e resultados.
- Declare limitações, decisões pendentes e riscos.
- Não esconda mudanças que não puderam ser concluídas.

# Handoff — transferência de contexto

## Objetivo
Continuar a construção do software de análise do pássaro bebedor para o relatório final, sem depender do histórico completo de conversas.

## Decisões já estabelecidas
- A análise final será reimplementada do zero segundo `ai-context/PROJECT.md`.
- `parcial/` é apenas registro histórico do relatório parcial. Não editar, reorganizar, apagar, refatorar ou integrar seus scripts.
- Cada subpasta de dados representa uma filmagem independente.
- Os quatro CSVs de entrada são `tracker.csv`, `massa.csv`, `mergulhadas.csv` e `condicoes.csv`.
- Os eventos de mergulho são selecionados manualmente; não detectar automaticamente cada oscilação.
- Períodos são diferenças entre tempos de eventos consecutivos.
- A massa pode ser interpolada no ponto médio de cada ciclo, sem extrapolação.
- O ajuste principal inicial da massa é linear global, acompanhado de resíduos e diagnósticos.
- Ajustes locais usam janelas fixas configuráveis, com padrão inicial de 200 s. Não selecionar janelas para forçar linearidade.
- A taxa positiva de perda de massa, quando a inclinação é negativa, é \(-b\) g/s ou \(-60b\) g/min.
- A resolução nominal de balança indicada no relatório parcial é 0,0001 g; o ruído durante o movimento pode ser maior.
- As seis responsabilidades de módulos estão especificadas em `PROJECT.md`; a localização acordada é a raiz do projeto.

## Contexto científico
Consultar `ai-context/EXPERIMENT.md`. A hipótese física não deve ser tratada como conclusão. O modelo relaciona aproximadamente o período ao inverso do produto entre calor latente e taxa de evaporação.

## Estado conhecido na preparação
- A implementação modular final ainda não estava implementada.
- Os dados reais disponíveis não aparentavam conter os quatro CSVs completos em cada filmagem.
- Existe uma pasta de exemplos com os quatro CSVs.
- Não há testes automatizados consolidados.

## Como retomar
1. Ler `AGENTS.md`, `CURRENT_STATE.md`, `TASKS.md`, `PROJECT.md` e `EXPERIMENT.md`.
2. Verificar o estado real do repositório, pois este handoff pode ficar desatualizado.
3. Não assumir que itens marcados como pendentes continuam pendentes sem inspecionar o código.
4. Executar somente a tarefa solicitada pelo usuário e suas dependências necessárias.
5. Atualizar `CURRENT_STATE.md`, `TASKS.md` e `LOG.md` ao concluir.

## Observação
Este arquivo é um resumo de decisões e contexto para transferência, não um registro de cada execução. Atualizá-lo apenas quando decisões, bloqueios ou contexto de continuidade mudarem significativamente.

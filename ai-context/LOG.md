# Registro de alterações

Este arquivo é cumulativo e append-only. Cada execução de trabalho acrescenta uma entrada curta ao final. Não reescrever nem apagar entradas anteriores. Não é necessário ler o histórico inteiro para acrescentar uma nova entrada.

## 2026-11-08 — Preparação do fluxo agêntico

### Alterações
- Criados os documentos de instruções, contexto científico, especificação do software, tarefas, estado atual e handoff.
- Registrada a proteção explícita da pasta `parcial/`.
- Formalizados os formatos de entrada, métodos de análise, saídas esperadas e arquitetura modular.

### Verificações
- Documentação inicial preparada com base no relatório parcial fornecido e nas decisões de arquitetura discutidas.

### Pendências
- Implementar o pipeline final.
- Completar os CSVs de entrada das filmagens reais.
- Criar e executar a suíte de testes.

## 2026-11-20 — Revisão documental do estado atual

### Alterações
- Alinhados README, instruções de agentes, especificação, estado atual, tarefas e handoff à estrutura real do pacote.
- Registrada a localização da implementação em `final/`, os seis módulos vazios e o papel limitado de `final/teste.py`.
- Atualizados os contratos documentais para os cabeçalhos CSV observados (`tempo_seg`, `temperatura_c`) e para a estrutura atual dos nove conjuntos de dados.
- Reforçada a proteção de `parcial/` e dos diretórios de dados brutos.

### Verificações
- Inventariados os arquivos Markdown fora de `parcial/`.
- Inspecionados os nomes, tamanhos e conteúdo dos módulos Python em `final/`.
- Conferidos cabeçalhos e contagens de linhas dos quatro CSVs nas nove filmagens reais e no conjunto de exemplo.
- Nenhum dado, script ou arquivo não-Markdown foi alterado.

### Pendências
- Implementação do pipeline e testes automatizados continuam pendentes.

# Análise do pássaro bebedor

Projeto de análise experimental da relação entre o líquido externo que umedece o feltro, a evaporação e o período de mergulho do pássaro bebedor.

## Estado desta versão

O conjunto de dados reais está em `final/dados/`: são nove filmagens (três por condição nominal: água, álcool 70% e álcool 99%). Cada uma contém `tracker.csv`, `massa.csv`, `mergulhadas.csv`, `condicoes.csv` e o arquivo de projeto do Tracker (`.trk`). Há também `final/dados_exemplo/`, com uma filmagem pequena para referência de formato, e `final/dados_old/`, uma cópia anterior dos CSVs.

Os módulos da implementação estão em `final/`. Nesta versão, a fundação está concluída: contratos das funções, convenção de janelas temporais (implementada em `periodos.py`) e uma suíte de testes. As demais funções têm apenas contratos e levantam `NotImplementedError`; a CLI ainda não processa dados. `final/teste.py` é apenas um reconhecedor estrutural de diretórios, não executa análise científica.

## Começar a trabalhar

Leia primeiro `AGENTS.md`. Em seguida, consulte `ai-context/CURRENT_STATE.md`, `ai-context/TASKS.md`, `ai-context/PROJECT.md` e `ai-context/EXPERIMENT.md`. `ai-context/HANDOFF.md` resume as decisões de continuidade.

A especificação técnica e o estado observado no repositório prevalecem sobre descrições antigas. Se código, dados ou documentação divergirem, inspecione o conteúdo atual e atualize os documentos afetados; não presuma que uma tarefa está concluída só porque foi planejada.

## Organização

- `final/`: implementação final, dados de entrada, exemplo e cópia antiga dos CSVs.
- `final/dados/`: nove filmagens reais, cada uma tratada como unidade independente.
- `final/dados_exemplo/`: exemplo reduzido de estrutura e formato.
- `final/dados_old/`: cópia anterior dos CSVs; não é entrada padrão.
- `ai-context/`: especificação, contexto científico, tarefas, estado e handoff.
- `parcial/`: registro histórico imutável. Não modificar nem usar como base de código.

## Instalação e testes

Requer Python 3.10 ou superior (testado somente em Python 3.12.3).

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
python -m pytest
```

## Execução

Validação das filmagens, a partir da raiz do repositório:

```bash
python -m final.analisar --diretorio final/dados --saida final/resultados --janela 200
```

Código de saída: 0 se todas são válidas, 1 se alguma é inválida, 2 para erro de uso. A análise científica ainda não está implementada.

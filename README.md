# Análise do pássaro bebedor

Projeto de análise experimental da relação entre o líquido externo que umedece o feltro, a evaporação e o período de mergulho do pássaro bebedor.

## Estado desta versão

O conjunto de dados reais está em `final/dados/`: são nove filmagens (três por condição nominal: água, álcool 70% e álcool 99%). Cada uma contém `tracker.csv`, `massa.csv`, `mergulhadas.csv`, `condicoes.csv` e o arquivo de projeto do Tracker (`.trk`). Há também `final/dados_exemplo/`, com uma filmagem pequena para referência de formato, e `final/dados_old/`, uma cópia anterior dos CSVs.

Os módulos da implementação estão em `final/`. Estão implementados e testados: validação das filmagens, cálculos de períodos, interpolação da massa, estatísticas, ajuste linear, ajustes por janela, pipeline completo com tabelas, gráficos e resumos. Resultados já gerados em `final/resultados/`. `final/teste.py` é apenas um reconhecedor estrutural de diretórios.

Prioridades 0–4 concluídas: fundação, validação, cálculos, pipeline/saídas e qualidade/validação ponta a ponta com documentação. A revisão amostral e os avisos de qualidade dos dados reais estão em `ai-context/REVISAO_QUALIDADE.md`.

## Começar a trabalhar

Leia primeiro `AGENTS.md`. Em seguida, consulte `ai-context/CURRENT_STATE.md`, `ai-context/TASKS.md`, `ai-context/PROJECT.md` e `ai-context/EXPERIMENT.md`. `ai-context/HANDOFF.md` resume as decisões de continuidade. Para qualidade dos dados e limitações, use `ai-context/REVISAO_QUALIDADE.md`.

A especificação técnica e o estado observado no repositório prevalecem sobre descrições antigas. Se código, dados ou documentação divergirem, inspecione o conteúdo atual e atualize os documentos afetados; não presuma que uma tarefa está concluída só porque foi planejada.

## Organização

- `final/`: implementação final, dados de entrada, exemplo e cópia antiga dos CSVs.
- `final/dados/`: nove filmagens reais, cada uma tratada como unidade independente.
- `final/dados_exemplo/`: exemplo reduzido de estrutura e formato.
- `final/dados_old/`: cópia anterior dos CSVs; não é entrada padrão.
- `final/resultados/`: saídas derivadas (não editar manualmente como se fossem dados brutos).
- `ai-context/`: especificação, contexto científico, tarefas, estado, handoff e revisão de qualidade.
- `parcial/`: registro histórico imutável. Não modificar nem usar como base de código.

## Instalação e testes

Requer Python 3.10 ou superior (testado somente em Python 3.12.3).

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
python -m pytest
```

Dependências de execução: `numpy`, `pandas`, `matplotlib` (ver `requirements.txt`). Versões mínimas são estimativas; o desenvolvimento usou numpy 2.x, pandas 2+/3.x e matplotlib 3.x.

## Execução

Validação e processamento de todas as filmagens, a partir da raiz do repositório:

```bash
python -m final.analisar --diretorio final/dados --saida final/resultados --janela 200
```

Para cada filmagem válida são gravados, em `final/resultados/<id>/`, tabelas CSV, `resumo.txt` e até quatro gráficos PNG. Código de saída: 0 se todas são válidas e processadas, 1 se alguma é inválida ou falhou, 2 para erro de uso.

## Formatos de saída (resumo)

- `periodos.csv`: ciclos entre mergulhos consecutivos, com ponto médio e massa interpolada (quando possível).
- `massa_ajuste.csv` / `massa_residuos.csv`: ajuste linear global e resíduos.
- `massa_por_janela.csv` / `periodo_por_janela.csv`: ajustes e estatísticas por janela fixa.
- `resumo.csv` / `resumo.txt`: identificação, condições, períodos, taxa, R², avisos e limitações.
- Gráficos: ângulo com mergulhos, massa + ajuste, período vs tempo, período vs massa (exploratório).

## Limitações

- O software produz estimativas e diagnósticos; não valida a hipótese física.
- R² é auxiliar; a adequação do modelo depende dos resíduos e do contexto experimental.
- Condições ambientais são um único registro por filmagem.
- Problemas de qualidade experimental (critério de anotação, movimento na balança, R² baixos em alguns álcoois) são documentados em `REVISAO_QUALIDADE.md` e não são mascarados pelo pipeline.
- Dados brutos e `parcial/` não são modificados.

# Dados e implementação da análise

A implementação final está organizada nesta pasta. Cada subpasta direta de `dados/` representa uma filmagem independente; seu nome é usado como identificador da saída, não como fonte autoritativa de metadados.

## Estrutura

```text
final/
├── analisar.py
├── pipeline.py
├── periodos.py
├── massa.py
├── graficos.py
├── relatorio.py
├── teste.py
├── dados/
│   └── id_da_filmagem/
│       ├── tracker.csv
│       ├── massa.csv
│       ├── mergulhadas.csv
│       ├── condicoes.csv
│       └── arquivo.trk
├── dados_exemplo/
├── dados_old/
└── resultados/  # saídas geradas pela execução
```

`dados/` contém nove filmagens reais, três para cada condição nominal. `dados_exemplo/` contém uma amostra de exemplo do formato dos dados, mas não será utilizada na análise. `dados_old/` é uma cópia anterior dos CSVs e não deve ser usada como entrada padrão.

## Formato dos CSVs

Os nomes de coluna abaixo são os que existem nos arquivos atuais:

- `tracker.csv`: `tempo_seg,angulo_deg` — observações de ângulo do Tracker.
- `massa.csv`: `tempo_seg,massa_g` — leituras de massa em instantes que podem não ser igualmente espaçados.
- `mergulhadas.csv`: `tempo_seg,angulo_deg` — eventos genuínos de mergulho selecionados manualmente. O instante do evento é `tempo_seg`; `angulo_deg` é o ângulo associado. Não há coluna `evento_id`.
- `condicoes.csv`: `liquido,dia,temperatura_c,umidade_pct` — exatamente uma linha de metadados por filmagem.

Não renomeie nem edite os CSVs originais para adaptar o software. A implementação deve ler esse formato. Não leia os arquivos .trk, utilize apenas os CSVs.

## Execução

A partir da raiz do repositório:

```bash
python -m final.analisar --diretorio final/dados --saida final/resultados --janela 200
```

**Estado:** pipeline completo. `analisar.py` valida e processa cada filmagem; `periodos.py` e `massa.py` calculam; `graficos.py` e `relatorio.py` gravam figuras e tabelas; `pipeline.py` orquestra uma filmagem. `teste.py` apenas reconhece e lista diretórios.

O comando acima valida as filmagens de `--diretorio`. Para validar outro conjunto, aponte `--diretorio` para outra pasta cujas subpastas tenham os quatro CSVs.

## Saídas por filmagem

Em `resultados/<id>/`:

- Tabelas: `periodos.csv`, `massa_ajuste.csv`, `massa_residuos.csv`, `massa_por_janela.csv`, `periodo_por_janela.csv`, `resumo.csv`
- Texto: `resumo.txt` (condições, períodos, taxa, R², avisos, limitações)
- Gráficos PNG: `angulo_mergulhos.png`, `massa_ajuste.png`, `periodo_tempo.png`, `periodo_massa_exploratorio.png`

## Testes

A partir da raiz do repositório, com as dependências de desenvolvimento instaladas (`pip install -r requirements-dev.txt`). Os módulos são importados como `final.<modulo>`:

```bash
python -m pytest
```

Os testes usam dados sintéticos e, em `test_dados_reais.py`, leem `dados/` somente em modo leitura (ou gravam em diretório temporário). Não alteram os originais.

Consulte `../AGENTS.md`, `../ai-context/PROJECT.md` e `../ai-context/REVISAO_QUALIDADE.md`. Os dados são imutáveis e `../parcial/` está fora do escopo de alteração.

## Limitações

- Estimativas e diagnósticos; não verificação da hipótese física.
- R² é auxiliar; examinar resíduos e contexto experimental.
- Condições ambientais: um registro por filmagem.
- Qualidade experimental (anotação, movimento na balança, R² baixos em alguns álcoois): ver `REVISAO_QUALIDADE.md`.

# Análise do pássaro bebedor

Cada subpasta de `dados/` representa uma filmagem e é analisada isoladamente. O nome da pasta não tem significado especial para o programa: é usado apenas para nomear a pasta correspondente em `resultados/`.

## Estrutura

```text
analise_passarinho/
├── analisar.py
├── dados/
│   └── nome_da_filmagem/
│       ├── tracker.csv
│       ├── massa.csv
│       ├── mergulhadas.csv
│       └── condicoes.csv
└── resultados/
    └── nome_da_filmagem/
        ├── tabelas/
        ├── graficos/
        └── resumo.txt
```

## CSVs de entrada

- `tracker.csv`: colunas `tempo_s,angulo_deg`; uma linha por medida do Tracker.
- `massa.csv`: colunas `tempo_s,massa_g`; uma linha por leitura, com intervalos que podem variar.
- `mergulhadas.csv`: colunas `evento_id,tempo_s`; instantes de mergulhadas reais identificados manualmente.
- `condicoes.csv`: uma linha com `liquido,dia,temperatura_C,umidade_pct`.

Exemplo de `condicoes.csv`:

```csv
liquido,dia,temperatura_C,umidade_pct
alcool 70%,2026-10-24,24.5,61
```

O campo `liquido` pode ser `alcool 70%`, `alcool 99%`, `agua` etc. O campo `dia` é texto livre: pode ser uma data, um número de sessão ou qualquer rótulo. Temperatura e umidade são os valores registrados para a filmagem.

## Execução prevista

```bash
python analisar.py --diretorio dados --saida resultados --janela 200
```

`--janela` define a duração das janelas temporais em segundos. O programa deve analisar cada subpasta de `dados/` separadamente e criar uma pasta de mesmo nome em `resultados/`. Não haverá combinação automática de dados entre filmagens.

**Nota:** `analisar.py` é, nesta etapa, apenas um ponto de entrada estrutural. A lógica estatística e os gráficos serão implementados em seguida.

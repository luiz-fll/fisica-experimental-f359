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
└── resultados/  # criado pela futura execução
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

O comando planejado, após implementação da CLI, será executado a partir da raiz do repositório:

```bash
python -m final.analisar --diretorio final/dados --saida final/resultados --janela 200
```

**Atenção:** nesta versão, a CLI (`analisar.py`) ainda não está implementada: ela retorna código 2 com aviso. Os módulos `pipeline.py`, `massa.py`, `graficos.py` e `relatorio.py` contêm apenas contratos; `periodos.py` implementa a convenção de janelas. `teste.py` apenas reconhece e lista diretórios. O comando acima documenta a interface pretendida e ainda não é executável como análise.

## Testes

A partir da raiz do repositório, com as dependências de desenvolvimento instaladas (`pip install -r requirements-dev.txt`). Os módulos são importados como `final.<modulo>`:

```bash
python -m pytest
```

Os testes usam dados sintéticos e não leem `dados/`.

Consulte `../AGENTS.md` e `../ai-context/PROJECT.md` antes de implementar. Os dados são imutáveis e `../parcial/` está fora do escopo de alteração.

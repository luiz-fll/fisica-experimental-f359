# Especificação do software de análise

## 1. Objetivo

Construir um pipeline reprodutível que processe cada filmagem do pássaro bebedor independentemente, estime períodos de mergulho e taxa de variação da massa, gere tabelas, gráficos e resumos e permita comparar resultados entre ensaios em etapa própria. O software produz estimativas e diagnósticos; não decide se a hipótese física é verdadeira.

## 2. Escopo e localização

- A implementação final reside em `final/`. Não mover os módulos para a raiz do repositório sem autorização.
- `parcial/` é registro histórico imutável e não é base de código. Não consultar, editar ou integrar seu conteúdo, exceto se o usuário pedir explicitamente contexto histórico.
- Dados brutos em `final/dados/`, `final/dados_exemplo/` e `final/dados_old/` são somente leitura.
- Cada subpasta direta de `final/dados/` representa uma filmagem independente. Não misturar observações em ajustes/estatísticas individuais.
- `final/dados_old/` é uma cópia anterior dos CSVs; não é entrada padrão.
- `final/dados_exemplo/` é referência estrutural reduzida, não validação científica.

## 3. Arquitetura

Os seis módulos ficam em `final/`:

```text
final/
  analisar.py       # CLI, descoberta, leitura e validação de filmagens
  pipeline.py       # orquestra uma filmagem
  periodos.py       # eventos, períodos e estatísticas de período
  massa.py          # ajustes da massa e taxas de variação
  graficos.py       # visualizações a partir de resultados calculados
  relatorio.py      # exportação de tabelas e resumos
  dados/
  dados_exemplo/
  dados_old/
  resultados/       # saída gerada; não é dado bruto
```

Responsabilidades:

**`analisar.py`**
- Interpretar argumentos da CLI.
- Validar diretórios e parâmetros.
- Descobrir subpastas de filmagem.
- Ler e validar os quatro CSVs obrigatórios.
- Processar cada filmagem isoladamente; avisar e continuar após erro individual.
- Não conter cálculos científicos nem código de gráficos.

**`pipeline.py`**
- Orquestrar o processamento de uma filmagem.
- Receber dados carregados e parâmetros explicitamente.
- Chamar os módulos de cálculo e apresentação.
- Não duplicar leitura nem cálculos.

**`periodos.py`**
- Calcular períodos entre eventos manuais consecutivos.
- Construir tabela de ciclos e associar massa interpolada no ponto médio, quando possível.
- Calcular estatísticas globais e por janela.
- Não detectar automaticamente mergulhos a partir do sinal do Tracker.

**`massa.py`**
- Ajustar modelo linear global \(m(t)=a+bt\).
- Calcular resíduos e diagnósticos.
- Calcular ajustes locais em janelas fixas, quando houver pontos suficientes.
- Quando \(b<0\), reportar taxa positiva de perda \(-b\) g/s e \(-60b\) g/min. Para \(b\geq0\), reportar a inclinação sem chamá-la de taxa positiva de evaporação.
- Não suavizar nem alterar observações.

**`graficos.py`**
- Gerar visualizações a partir de tabelas e parâmetros calculados.
- Não recalcular períodos, ajustes ou estatísticas.
- Incluir unidades e identificação da filmagem; salvar em sua pasta de resultados.

**`relatorio.py`**
- Exportar CSVs derivados e resumos.
- Não repetir cálculos.
- Preservar precisão numérica nos arquivos; arredondar apenas para apresentação.

## 4. Formato real dos dados

Os cabeçalhos abaixo foram verificados no pacote recebido. A implementação deve aceitá-los sem renomear ou editar os dados originais.

Cada filmagem contém:

### `tracker.csv`

Colunas: `tempo_seg`, `angulo_deg`.
- `tempo_seg`: tempo em segundos.
- `angulo_deg`: ângulo em graus.
- Uma linha por observação angular do Tracker.

### `massa.csv`

Colunas: `tempo_seg`, `massa_g`.
- `tempo_seg`: instante da leitura em segundos.
- `massa_g`: massa em gramas.
- O intervalo entre leituras pode variar; usar os tempos registrados, nunca criar frequência fixa fictícia.

### `mergulhadas.csv`

Colunas: `tempo_seg`, `angulo_deg`.
- Cada linha representa um mergulho genuíno selecionado manualmente pelo pesquisador.
- `tempo_seg` é o instante usado para calcular os períodos.
- `angulo_deg` registra o ângulo associado ao evento.
- Não existe coluna `evento_id` nos arquivos atuais. Se for necessário identificar eventos, o programa pode gerar identificadores derivados em memória/saída, sem alterar o CSV original.
- Não substituir seleção manual por detecção automática.

### `condicoes.csv`

Colunas: `liquido`, `dia`, `temperatura_c`, `umidade_pct`.
- Exatamente uma linha por filmagem.
- `liquido`: identificação textual do líquido.
- `dia`: texto livre (data, sessão ou rótulo).
- `temperatura_c`: temperatura em °C.
- `umidade_pct`: umidade relativa em %.
- Não inferir séries temporais a partir de um único registro. Explicitar aproximação de condições constantes quando adotada.

O conjunto atual possui nove filmagens em `final/dados/`, três por condição nominal. O nome da pasta é identificador, não fonte autoritativa de metadados.

## 5. Validação

Implementada em `final/analisar.py` (Prioridade 1). Validação em memória; nenhum arquivo é criado, alterado ou corrigido. O `.trk` nunca é lido. Cada CSV é lido uma única vez por filmagem.

**Erros** (a filmagem é inválida e não é processada):
- arquivo ausente, vazio, sem linhas de dados, não UTF-8 ou não legível;
- cabeçalho diferente do esperado (exato, na mesma ordem): `tracker.csv` = `tempo_seg,angulo_deg`; `massa.csv` = `tempo_seg,massa_g`; `mergulhadas.csv` = `tempo_seg,angulo_deg`; `condicoes.csv` = `liquido,dia,temperatura_c,umidade_pct`;
- número de campos inconsistente em alguma linha;
- campo vazio, valor não numérico, `nan` ou `inf` (linha identificada);
- tempos anteriores à origem (0 s), duplicados ou não ordenados (linhas identificadas);
- `tracker.csv` com menos de 2 registros; `massa.csv` com menos de 3 leituras (`MIN_LEITURAS_AJUSTE`); `mergulhadas.csv` com menos de 2 mergulhos (`MIN_MERGULHOS_PARA_PERIODO`);
- `condicoes.csv` com número de linhas diferente de 1, líquido ou dia vazios, temperatura ou umidade não numéricas ou não finitas, umidade fora de [0, 100].

**Avisos** (a filmagem é válida, o aviso é reportado):
- valores com espaços ao redor, aceitos sem alteração;
- mergulhos fora do intervalo de `tracker.csv` ou de `massa.csv` (sem massa interpolada, quando fora da massa);
- ângulo do mergulho a mais de `TOLERANCIA_ANGULO_EVENTO_GRAUS` = 2,0° do ângulo do tracker no mesmo instante.

Mensagens identificam filmagem e arquivo. Uma filmagem inválida não interrompe o lote: falhas inesperadas também são isoladas (status `erro_inesperado`).

Não há correção silenciosa. Problemas de qualidade dos dados que não são erros de formato (saltos de massa, critério de anotação, sincronização temporal) não são verificados aqui; ver `revisao_dados_e_plano.md`.

## 6. Métodos

### 6.1 Períodos e massa por ciclo

Para eventos consecutivos \(t_i\) e \(t_{i+1}\):

\[
T_i=t_{i+1}-t_i
\]

A tabela de ciclos deve conter, no mínimo:
- índice/identificador derivado do evento inicial e final;
- tempos inicial e final;
- ponto médio temporal;
- período em segundos;
- massa interpolada no ponto médio, se houver suporte.

Interpolar linearmente a massa no ponto médio temporal, somente dentro do domínio coberto por `massa.csv`. Não extrapolar. Sem suporte, deixar ausente e registrar diagnóstico.

### 6.2 Estatísticas globais

Quando houver ciclos: quantidade, média, desvio-padrão amostral, mínimo e máximo. Informar o número de ciclos e evitar caracterizar estatísticas de amostras pequenas como robustas.

### 6.3 Janelas temporais

- Duração padrão inicial: 200 s, configurável pela CLI.
- Definir janelas a partir da origem temporal do ensaio, com intervalos semiabertos e convenção explícita para o último limite.
- Usar a mesma duração para ajustes locais de massa e agregação temporal de períodos.
- Atribuir cada ciclo à janela que contém seu ponto médio.
- Não escolher janelas após observar os resultados para forçar linearidade.
- Janelas sem dados suficientes devem ter diagnóstico ou ser omitidas por regra documentada.

**Convenção adotada (definida na fundação; implementada em `final/periodos.definir_limites_janelas` e `final/periodos.atribuir_janela`):**

- Origem fixa em 0 s, referência comum dos `tempo_seg`. Não é reancorada por arquivo.
- Janelas `[início, fim)` de duração `L` (padrão 200 s), exceto a última.
- Número de janelas: `N = max(1, floor(t_fim / L))`, em que `t_fim` é o maior instante de `massa.csv` ou `mergulhadas.csv` da própria filmagem. Não é escolhido a partir dos resultados.
- A última janela absorve o resto do ensaio: `[(N-1)·L, t_fim]`, fechada à direita. Ela tem duração entre `L` e `2L`. Assim, um resto de poucos milissegundos após 600 s não gera janela própria.
- Cada ciclo pertence à janela que contém seu ponto médio; instantes fora de `[0, t_fim]`, negativos ou não finitos não pertencem a nenhuma janela.
- Janelas numeradas de 1 a N e sempre listadas nas tabelas, mesmo quando vazias ou insuficientes.
- Decisão tomada pelo pesquisador (2026-11-20): a última janela absorve o resto (alternativa à convenção `ceil`, que criava janelas com uma única leitura). Com os nove conjuntos reais, obtém-se 3 janelas com 9, 10 e 11 leituras de massa cada.

Para cada janela, reportar quantidade de leituras, inclinação, taxa em g/min quando aplicável, R² e diagnóstico da massa; para períodos, quantidade, média, desvio-padrão, mínimo e máximo quando disponíveis.

### 6.4 Ajuste de massa

Modelo principal inicial:

\[
m(t)=a+bt
\]

\(b\) é a variação de massa em g/s. Se \(b<0\), a taxa positiva de perda é:

\[
r=-b\ [g/s], \qquad r_{min}=-60b\ [g/min]
\]

Produzir ajuste global e ajustes locais por janela quando houver pontos suficientes. Mínimos definidos na fundação (`massa.py`): `MIN_LEITURAS_AJUSTE = 3` leituras finitas com tempos distintos para estimar `a` e `b`; janelas abaixo disso recebem o status `leituras_insuficientes`, sem valores ajustados, e permanecem na tabela. `LEITURAS_RECOMENDADAS_AJUSTE = 5`: com 3 ou 4 leituras o ajuste é calculado, mas recebe o diagnóstico `poucos_pontos` (1 grau de liberdade residual ou menos). Calcular resíduos \(m_{obs}-m_{ajustado}\). R² é diagnóstico auxiliar, nunca critério isolado.

Não aplicar filtros, remoção de outliers ou suavização como padrão. Métodos alternativos devem ser complementares e identificados.

## 7. Saídas planejadas

Para cada filmagem válida, gerar `resultados/<id_da_filmagem>/`, com pelo menos:
- `periodos.csv`;
- `massa_ajuste.csv`;
- `massa_por_janela.csv`;
- `periodo_por_janela.csv`;
- `resumo.csv`;
- `resumo.txt`;
- gráficos aplicáveis: ângulo × tempo com mergulhos marcados; massa × tempo com ajuste global; período × tempo; período × massa interpolada (exploratório); diagnósticos por janela quando úteis.

Não gerar gráfico sem dados suficientes; registrar motivo no resumo. Saídas nunca devem ser gravadas sobre os dados brutos.

## 8. CLI

Execução a partir da raiz do repositório:

```bash
python -m final.analisar --diretorio final/dados --saida final/resultados --janela 200
```

- `--diretorio` (padrão: `final/dados`): pasta com as subpastas de filmagem.
- `--saida` (padrão: `final/resultados`): diretório-base dos resultados; não pode estar dentro de `--diretorio`.
- `--janela` (padrão: 200): duração positiva e finita, em segundos.

**Estado atual:** a CLI realiza a validação de todas as filmagens e imprime uma tabela com status, quantidade de leituras, mergulhos, avisos e erros, com a identificação de arquivo e linha. Não grava resultados: o processamento científico e a gravação em `--saida` dependem das Prioridades 2 e 3.

Códigos de saída: 0 se todas as filmagens são válidas; 1 se alguma é inválida; 2 para erro de uso ou de configuração (diretório inexistente, saída dentro dos dados, janela inválida, nenhuma subpasta).

## 9. Contratos entre módulos

Assinaturas definidas na fundação (docstrings nos módulos; `NotImplementedError` onde a lógica ainda não existe):

| Módulo | Funções | Situação |
|---|---|---|
| `periodos.py` | `definir_limites_janelas`, `atribuir_janela` | implementadas e testadas |
| `periodos.py` | `construir_ciclos`, `interpolar_massa`, `estatisticas_periodos`, `periodos_por_janela` | contrato |
| `massa.py` | `ajustar_linear`, `taxa_de_perda`, `ajustar_janelas` | contrato |
| `pipeline.py` | `processar_filmagem(filmagem, duracao_janela_s, pasta_saida)` | contrato |
| `graficos.py` | `plotar_angulo_mergulhos`, `plotar_massa_ajuste`, `plotar_periodo_tempo`, `plotar_periodo_massa` | contrato |
| `relatorio.py` | `gravar_tabelas`, `gravar_resumo_texto` | contrato |
| `analisar.py` | `main`, `descobrir_filmagens`, `carregar_filmagem`, `validar_lote`, `Problema`, `ErroFilmagem` | implementadas e testadas (Prioridade 1) |

Convenção de importação: os módulos estão em `final/`, que é um pacote Python. Importar sempre como `from final.periodos import ...`; execução pela raiz do repositório com `python -m final.analisar`. Os testes configuram a raiz do repositório em `pytest.ini` (`pythonpath = .`).

Filmagem como dicionário (contrato entre `analisar.py` e `pipeline.py`): chaves `id` (str), `pasta` (Path), `tracker`, `massa`, `mergulhadas` (DataFrames com as colunas do cabeçalho real, valores `float`), `condicoes` (dicionário com `liquido`, `dia`, `temperatura_c`, `umidade_pct`) e `avisos` (lista de `Problema`). `carregar_filmagem` levanta `ErroFilmagem(pasta, problemas)` com todos os problemas quando há erro; `Problema` tem `arquivo`, `gravidade` (`"erro"` ou `"aviso"`) e `mensagem`. `validar_lote(pastas)` devolve, para cada pasta, `id`, `pasta`, `status` (`valida`, `invalida`, `erro_inesperado`), `filmagem` e `problemas`. Não há classe compartilhada, para evitar importações circulares.

- `analisar.py` lê/valida cada filmagem uma vez.
- Dados e metadados carregados são passados explicitamente ao pipeline.
- `pipeline.py` coordena funções e recebe resultados estruturados.
- `periodos.py` e `massa.py` recebem DataFrames/arrays e retornam tabelas/dicionários.
- `graficos.py` recebe resultados prontos.
- `relatorio.py` recebe resultados prontos e grava arquivos.
- Evitar importações circulares.
- Definir nomes exatos de funções e estruturas na implementação, docstrings e testes.

## 10. Testes mínimos

Criar testes para períodos, interpolação sem extrapolação, ajuste linear sintético, conversão/sinal da taxa, limites de janelas, dados insuficientes, tempos duplicados/desordenados, múltiplas filmagens, continuidade após falha individual e geração de saídas. Dados sintéticos validam o código, não substituem validação científica com dados reais.

## 11. Critérios de conclusão

A primeira versão será funcional quando processar uma e várias filmagens, isolar falhas, gerar tabelas/gráficos aplicáveis, possuir testes para cálculos e casos-limite, documentar dependências/execução e preservar integralmente os dados brutos e `parcial/`.

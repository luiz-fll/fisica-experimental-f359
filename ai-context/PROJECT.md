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

Validar em memória; não criar CSVs intermediários de validação. Verificar:
- existência e legibilidade dos quatro arquivos;
- colunas obrigatórias, aceitando os nomes exatos acima;
- tipos numéricos e valores finitos;
- tempos coerentes e ordenáveis;
- duplicatas temporais e possíveis efeitos;
- pelo menos dois eventos para calcular períodos;
- leituras suficientes para ajustes;
- eventos dentro/fora do domínio temporal dos dados;
- exatamente uma linha em `condicoes.csv`.

Não corrigir dados silenciosamente. Mensagens devem identificar filmagem e arquivo. Uma filmagem inválida deve ser ignorada sem interromper as demais.

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

Produzir ajuste global e ajustes locais por janela quando houver pontos suficientes. O mínimo local deve ser definido e documentado durante a implementação; valor inicial sugerido: três pontos. Calcular resíduos \(m_{obs}-m_{ajustado}\). R² é diagnóstico auxiliar, nunca critério isolado.

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

## 8. CLI planejada

A interface inicial planejada é:

```bash
python final/analisar.py --diretorio final/dados --saida final/resultados --janela 200
```

- `--diretorio`: diretório que contém subpastas de filmagem.
- `--saida`: diretório-base dos resultados.
- `--janela`: duração positiva da janela em segundos.

Esta CLI é uma especificação, não uma funcionalidade disponível nesta versão: `analisar.py` está vazio. Não documentar execução como funcional antes de implementar e testar.

## 9. Contratos entre módulos

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

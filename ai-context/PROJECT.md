# Especificação do software de análise

## 1. Objetivo

Construir um pipeline reprodutível que processe cada filmagem do pássaro bebedor de forma independente, estime períodos de mergulho e taxa de variação da massa, gere tabelas, gráficos e resumos e permita comparar os resultados entre ensaios posteriormente.

O software não decide se a hipótese física é verdadeira. Ele produz estimativas, diagnósticos e visualizações para interpretação científica.

## 2. Escopo e limites

- A implementação final será refeita de acordo com esta especificação.
- `parcial/` é histórico do relatório parcial e está fora do escopo de edição. Nunca alterar ou integrar seus scripts.
- Não misturar observações de filmagens diferentes em ajustes ou estatísticas individuais.
- Comparações entre filmagens podem ser feitas em etapa própria futura, mantendo cada resultado individual identificável.
- Os dados brutos permanecem imutáveis.

## 3. Arquitetura desejada

Os seis módulos Python ficam na raiz do projeto:

```text
analisar.py       # CLI, descoberta e validação de filmagens
pipeline.py       # orquestra uma filmagem
periodos.py       # eventos, períodos e estatísticas de período
massa.py          # ajustes da massa e taxas de variação
graficos.py       # visualizações a partir de resultados calculados
relatorio.py      # exportação de tabelas e resumos
```

Também haverá `tests/`, `dados/` e `resultados/`. Não criar módulos adicionais sem necessidade demonstrada e justificativa.

### Responsabilidades

**`analisar.py`**
- Interpretar argumentos de linha de comando.
- Validar diretórios e parâmetros gerais.
- Descobrir subpastas de filmagem em `dados/`.
- Validar os quatro CSVs obrigatórios de cada filmagem.
- Processar cada filmagem isoladamente, avisando e continuando quando uma estiver inválida.
- Não conter cálculos científicos nem código de gráficos.

**`pipeline.py`**
- Orquestrar o processamento de uma filmagem.
- Receber dados já carregados e parâmetros.
- Chamar funções de `periodos.py`, `massa.py`, `graficos.py` e `relatorio.py`.
- Não duplicar cálculos nem leitura de arquivos.

**`periodos.py`**
- Calcular períodos entre eventos consecutivos de mergulho.
- Construir tabela de ciclos.
- Associar a cada ciclo a massa interpolada no ponto médio, quando possível.
- Calcular estatísticas globais e por janela temporal.
- Não identificar automaticamente mergulhos a partir de oscilações: os eventos de `mergulhadas.csv` são identificados manualmente pelo pesquisador.

**`massa.py`**
- Ajustar modelo linear global \(m(t)=a+bt\).
- Calcular taxa positiva de perda de massa \(-b\), em g/s e g/min, se a inclinação for negativa.
- Produzir valores ajustados e resíduos.
- Calcular ajustes locais por janelas fixas quando houver pontos suficientes.
- Reportar número de pontos, inclinação, taxa, R² e diagnóstico/resíduos.
- Não alterar nem suavizar silenciosamente os dados observados.

**`graficos.py`**
- Gerar gráficos a partir das tabelas e parâmetros já calculados.
- Não recalcular períodos, ajustes ou estatísticas.
- Incluir unidades, identificação da filmagem e condições ambientais nos títulos/subtítulos ou legendas.
- Salvar figuras na pasta de resultados da filmagem.

**`relatorio.py`**
- Exportar CSVs derivados e resumos TXT.
- Não repetir cálculos científicos.
- Preservar precisão numérica suficiente nos arquivos de dados; arredondamento para apresentação deve ocorrer apenas no texto/visualização.

## 4. Organização dos dados

Cada subpasta direta de `dados/` representa uma filmagem independente. O nome é um identificador opaco: não inferir líquido, dia ou pássaro a partir do nome. Esses metadados vêm de `condicoes.csv`.

Formato obrigatório:

```text
dados/
  nome_livre_da_filmagem/
    tracker.csv
    massa.csv
    mergulhadas.csv
    condicoes.csv
```

### `tracker.csv`

Colunas obrigatórias:
- `tempo_s`: tempo em segundos.
- `angulo_deg`: ângulo em graus.

Cada linha representa uma observação do rastreamento angular. Tempos devem ser numéricos e ordenáveis. Não se deve presumir que os pontos estejam sempre espaçados igualmente.

### `massa.csv`

Colunas obrigatórias:
- `tempo_s`: instante da leitura em segundos.
- `massa_g`: massa observada em gramas.

O intervalo entre leituras pode variar. Usar os tempos registrados; nunca criar uma frequência fixa fictícia. A resolução nominal declarada no relatório parcial é 0,0001 g, mas o ruído dinâmico pode ser maior. Preservar os valores originais.

### `mergulhadas.csv`

Colunas obrigatórias:
- `evento_id`: identificador do evento.
- `tempo_s`: instante de cada mergulho genuíno, anotado manualmente.

A tabela contém mergulhos selecionados pelo pesquisador, não todos os pequenos extremos ou oscilações. Não substituir a seleção manual por detecção automática sem pedido explícito.

### `condicoes.csv`

Exatamente uma linha com:
- `liquido`: identificação textual do líquido externo.
- `dia`: texto livre para data, sessão ou identificação do dia.
- `temperatura_C`: temperatura em °C.
- `umidade_pct`: umidade relativa em %.

Temperatura e umidade são metadados por filmagem. Não interpolar nem inventar séries temporais a partir de um único registro. A aproximação de condições constantes deve ser explicitada no relatório quando adotada.

## 5. Validação dos dados

Validar em memória; não criar CSVs intermediários de validação.

Verificar:
- existência e legibilidade dos quatro arquivos;
- presença das colunas obrigatórias;
- tipos numéricos nas colunas quantitativas;
- ausência de valores não finitos;
- tempos coerentes e ordenáveis;
- duplicatas temporais, informando quando possam afetar cálculos;
- pelo menos dois eventos para calcular um período;
- número suficiente de leituras para ajuste;
- eventos dentro ou fora do intervalo de dados, com aviso;
- uma única linha em `condicoes.csv`.

Não corrigir silenciosamente dados inválidos. Mensagens devem identificar a filmagem e o arquivo. Uma filmagem inválida deve ser ignorada sem impedir o processamento das demais.

## 6. Métodos de análise

### 6.1 Períodos de mergulho

Para eventos consecutivos \(t_i\) e \(t_{i+1}\):

\[
T_i=t_{i+1}-t_i
\]

A tabela de ciclos deve conter, no mínimo:
- `evento_inicio_id`
- `evento_fim_id`
- `tempo_inicio_s`
- `tempo_fim_s`
- `tempo_medio_s` (ponto médio temporal)
- `periodo_s`
- `massa_interpolada_g`

Interpolar linearmente a massa observada no ponto médio temporal do ciclo, desde que esse instante esteja dentro do domínio coberto pelas leituras de massa. Não extrapolar. Se não houver suporte para interpolação, deixar o valor ausente e registrar diagnóstico.

### 6.2 Estatísticas globais de período

Calcular, quando houver ciclos:
- quantidade de períodos;
- média;
- desvio-padrão amostral;
- mínimo e máximo.

Não apresentar estatísticas como robustas quando a amostra for pequena. Informar o número de ciclos.

### 6.3 Análise temporal por janelas

Usar janelas de duração fixa, com padrão inicial de 200 s e parâmetro configurável pela CLI. As janelas devem ser definidas a partir da origem temporal do ensaio, com convenção explícita e consistente (intervalos semiabertos, exceto eventual último limite).

A mesma duração configurada deve orientar a análise local de massa e a agregação temporal de períodos. Não escolher janelas após observar os dados para obter melhor linearidade.

Para cada janela:
- massa: número de leituras, inclinação, taxa em g/min, R² e diagnóstico;
- período: quantidade de ciclos e média, desvio-padrão, mínimo e máximo, quando disponíveis.

Atribuir um ciclo à janela que contém seu ponto médio temporal. Janelas sem dados suficientes devem aparecer com diagnóstico ou ser omitidas segundo regra documentada, sem inventar valores.

### 6.4 Ajuste da massa

Modelo principal inicial:

\[
m(t)=a+bt
\]

A inclinação \(b\) é a variação de massa em g/s. Quando \(b<0\), a taxa positiva de perda de massa é:

\[
r=-b \quad [g/s], \qquad r_{min}=-60b \quad [g/min]
\]

Se a inclinação for positiva, não chamar \(-b\) de taxa positiva de evaporação; reportar a inclinação observada e sinalizar que a interpretação como perda de massa não se aplica diretamente.

Produzir ajuste global para toda a filmagem e ajustes locais por janela quando houver quantidade mínima configurada/justificada de pontos (padrão inicial sugerido: pelo menos 3, sujeito a decisão de implementação). Calcular resíduos \(m_{obs}-m_{ajustado}\). R² é diagnóstico auxiliar, não critério único de aceitação.

Não aplicar filtros, remoção de outliers ou suavização como padrão. Métodos alternativos podem ser acrescentados como análises complementares, claramente identificadas e sem substituir o método principal.

## 7. Saídas por filmagem

Cada filmagem válida deve produzir uma pasta `resultados/<nome_da_filmagem>/` contendo, no mínimo:

- `periodos.csv`: tabela de ciclos e massa interpolada.
- `massa_ajuste.csv`: tempo, massa observada, massa ajustada global e resíduo.
- `massa_por_janela.csv`: parâmetros/diagnósticos do ajuste em cada janela.
- `periodo_por_janela.csv`: estatísticas dos períodos por janela.
- `resumo.csv`: resumo estruturado de metadados e resultados globais.
- `resumo.txt`: resumo legível, incluindo avisos e limitações.
- gráficos:
  1. ângulo × tempo, com mergulhos marcados;
  2. massa × tempo, com ajuste global;
  3. período × tempo;
  4. período × massa interpolada (exploratório);
  5. diagnósticos por janela, quando úteis.

Os nomes dos arquivos devem ser estáveis e documentados. Não gerar gráficos que não tenham dados suficientes; registrar o motivo no resumo.

## 8. CLI prevista

Exemplo:

```bash
python analisar.py --diretorio dados --saida resultados --janela 200
```

- `--diretorio`: diretório que contém subpastas de filmagem.
- `--saida`: diretório-base dos resultados.
- `--janela`: duração da janela em segundos, positiva.

A CLI pode ganhar opções adicionais justificadas, mantendo defaults documentados.

## 9. Contratos entre módulos

- `analisar.py` lê e valida os dados uma vez por filmagem.
- Dados carregados e metadados são passados explicitamente ao pipeline.
- `pipeline.py` coordena chamadas e recebe resultados estruturados.
- `periodos.py` e `massa.py` recebem DataFrames/arrays e retornam DataFrames e dicionários de resumo.
- `graficos.py` recebe dados e resultados prontos; não recalcula.
- `relatorio.py` recebe resultados prontos e grava arquivos.
- Evitar importações circulares.

Os nomes exatos das funções e estruturas devem ser definidos durante a implementação e documentados em docstrings e testes.

## 10. Testes mínimos

Criar testes para:
- períodos entre eventos e estatísticas;
- interpolação dentro do domínio e ausência de extrapolação;
- ajuste linear com dados sintéticos conhecidos;
- conversão g/s para g/min e sinal da taxa;
- janelas e limites temporais;
- dados insuficientes;
- tempos duplicados/desordenados;
- processamento isolado de múltiplas filmagens;
- continuidade do lote quando uma filmagem é inválida;
- geração das saídas esperadas.

Os testes sintéticos validam o código, não substituem validação com dados reais.

## 11. Critérios de conclusão do projeto

A primeira versão é considerada funcional quando:
1. processa uma filmagem válida de ponta a ponta;
2. processa várias filmagens isoladamente;
3. ignora filmagem inválida com aviso e continua;
4. gera todas as tabelas e gráficos aplicáveis;
5. tem testes para cálculos e casos-limite;
6. documenta dependências e comando de execução;
7. não altera dados brutos nem `parcial/`.

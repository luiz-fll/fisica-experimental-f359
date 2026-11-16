# Experimento: pássaro bebedor

## 1. Pergunta de pesquisa

Como a taxa de evaporação e o calor latente do líquido externo que umedece o feltro — água, álcool etílico 70% e álcool isopropílico 99% — alteram o período \(\tau\) do ciclo de mergulho do pássaro bebedor?

A variável independente prática é o líquido externo utilizado. A variável dependente é o período do ciclo de mergulho. A taxa de variação da massa associada à evaporação é estimada a partir de \(m_e(t)\). Temperatura e umidade relativa do ar são monitoradas porque afetam a evaporação.

## 2. Funcionamento físico descrito no relatório parcial

O brinquedo contém um tubo com bulbos de vidro nas extremidades e diclorometano (\(CH_2Cl_2\)) como fluido interno, em equilíbrio com seu vapor. A evaporação do líquido externo no feltro resfria a cabeça. Parte do vapor interno condensa e a pressão de vapor na cabeça diminui em relação à pressão no corpo. A diferença de pressão desloca o líquido interno tubo acima, movendo o centro de massa para a frente até o pássaro tombar.

Quando o pássaro se inclina, a extremidade inferior do tubo emerge do líquido. Uma bolha de vapor sobe, as pressões se aproximam e o líquido retorna ao corpo. O torque gravitacional restaura a posição vertical. O ciclo se repete enquanto o feltro permanecer úmido.

O pássaro é tratado conceitualmente como máquina térmica entre a cabeça resfriada e o corpo à temperatura ambiente e, mecanicamente, como um pêndulo composto de massa variável. O projeto não pretende modelar integralmente a dinâmica rotacional; ela define o evento observado (o mergulho).

## 3. Conceitos e modelo físico de trabalho

### Termodinâmica
A evaporação do líquido externo retira calor da cabeça por meio do calor latente. O resfriamento está relacionado à mudança da pressão de vapor do fluido interno, discutida no relatório por meio da relação de Clausius–Clapeyron.

### Transporte de massa
A taxa de evaporação depende, entre outros fatores, da pressão de vapor, massa molar, umidade relativa e convecção. Para a água, o relatório parcial considera uma dependência com a umidade relativa \(H\), representada heuristicamente por:

\[
\frac{dm_e}{dt}=\kappa(100-H)^\beta
\]

em que \(\kappa\) e \(\beta\) são parâmetros. Essa expressão é uma hipótese/modelo simplificado do relatório, não uma calibração estabelecida pelo software.

### Relação proposta para o período
Se \(\Delta m_e\) é a massa evaporada necessária para produzir o resfriamento associado a um ciclo, \(L_e\) é o calor latente específico e \(C\) é uma capacidade térmica efetiva, o relatório apresenta a relação aproximada:

\[
\tau \approx \frac{C|\Delta T|}{L_e\,|dm_e/dt|}
\]

Assim, para um mesmo pássaro e sob as aproximações adotadas:

\[
\tau \propto \frac{1}{L_e\,|dm_e/dt|}
\]

A relação é uma previsão simplificada. O código deve estimar as grandezas observáveis; não deve assumir que a relação foi comprovada.

## 4. Hipóteses registradas

- **H1:** a ordem dos períodos acompanha a relação inversa entre calor latente e taxa de evaporação, isto é, \(\tau \propto [L_e |dm_e/dt|]^{-1}\), dentro das aproximações do modelo.
- **H2:** previsão de ordenação: \(\tau(\text{isopropílico 99\%}) < \tau(\text{etanol 70\%}) < \tau(\text{água})\).

O relatório parcial usa propriedades de massa molar, pressão de vapor e calor latente para estimar uma ordem esperada. A previsão para etanol 70% é especialmente incerta porque é uma mistura água–etanol, pode desviar da idealidade e sua composição pode mudar durante a evaporação. Os valores tabulados e cálculos do relatório devem ser tratados como conteúdo do relatório parcial, sujeitos a revisão científica, não como constantes codificadas no programa.

## 5. Aparato descrito no relatório parcial

- Três pássaros bebedores, um destinado a cada líquido.
- Água, álcool etílico 70% e álcool isopropílico 99%.
- Béquer de 200 mL.
- Balança digital com resolução declarada de 0,0001 g.
- Termo-higrômetro digital, precisão declarada de ±1 °C e ±5% para umidade.
- Celular em tripé, filmagem lateral a 30 FPS.
- Marcação no pescoço do pássaro para rastreamento no Tracker.

Essas especificações reproduzem o relatório parcial. Se o aparato ou as especificações efetivamente usadas no conjunto final forem diferentes, registrar a alteração com evidência e atualizar este documento mediante decisão do usuário.

## 6. Procedimento descrito no relatório parcial

1. Posicionar a câmera lateralmente, enquadrando o pássaro na balança e os mostradores de massa, temperatura e umidade.
2. Colocar o líquido externo no béquer e mergulhar completamente a cabeça do pássaro por 30 s.
3. Colocar o pássaro na balança e mantê-lo inicialmente tombado.
4. Soltar o pássaro e filmar seu movimento, a massa e as condições ambientais por aproximadamente 10 min.
5. Repetir o procedimento para os outros pássaros/líquidos, lavando o béquer entre ensaios.
6. Rastrear o ângulo no Tracker, identificar os eventos de mergulho e obter leituras de massa ao longo do tempo.

O relatório parcial registra a intenção de refazer filmagens com a caixa da balança aberta para reduzir saturação do ar com vapor do líquido. Também observa que o termo-higrômetro não estava dentro da caixa, de modo que as condições medidas podem não representar o ambiente interno. Isso deve permanecer como limitação experimental enquanto não houver novos registros que resolvam a questão.

## 7. Limitações experimentais relevantes

- O movimento do pássaro afeta a estabilidade e a precisão das leituras da balança.
- A resolução nominal da balança não equivale à incerteza efetiva de cada leitura durante o movimento.
- Temperatura e umidade são medições ambientais com precisão limitada; um valor único por filmagem é uma aproximação se as condições forem consideradas estáveis.
- A medição externa pode não representar o microambiente dentro da caixa da balança.
- Foram usados pássaros diferentes para os líquidos, o que pode introduzir diferenças na capacidade térmica efetiva \(C\), na geometria e no comportamento.
- A mistura etanol 70% pode alterar sua composição durante o ensaio.
- A identificação dos mergulhos é manual e pode introduzir incerteza temporal.
- Um intervalo de observação finito e poucos ciclos podem limitar estatísticas e tendências.

## 8. Distinção entre relatório parcial e análise final

O diretório `parcial/` contém análise exploratória e materiais usados para o relatório parcial. É um registro histórico imutável para o agente: não deve ser alterado nem usado como base de código para a arquitetura final.

A análise final será reimplementada do zero, seguindo `PROJECT.md`. O relatório parcial pode ser consultado como registro do que foi feito, mas seus resultados não devem ser tratados como resultados finais nem incorporados automaticamente.

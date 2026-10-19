"""Análise do pássaro bebedor no intervalo de 400 a 600 s.

Entradas na mesma pasta:
- alcool70_dia2.txt: exportação do Tracker, com colunas t, x, y, θ

As massas e os instantes das mergulhadas abaixo são as anotações manuais
fornecidas para este intervalo. O script gera gráficos, tabelas CSV e um resumo.
Requer: pandas, numpy e matplotlib.
"""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

PASTA = Path(__file__).resolve().parent
ARQUIVO_TRACKER = PASTA / "alcool70_dia2.txt"
INICIO_S = 400.0
FIM_S = 600.0

# Instantes das mergulhadas identificadas manualmente (segundos)
tempos_mergulhos = np.array([
    402.1, 423.633, 445.3, 466.7, 487.1,
    505.733, 525.5, 547.0, 569.267, 592.3
], dtype=float)

# Leituras manuais de massa (g), fornecidas a cada 10 s
massa = pd.DataFrame({
    "t_s": [400, 410, 420, 430, 440, 450, 460, 470, 480, 490, 500,
            510, 520, 530, 540, 550, 560, 570, 580, 590, 600],
    "m_g": [40.6950, 40.6920, 40.6879, 40.6843, 40.6809, 40.6778,
            40.6738, 40.6768, 40.6667, 40.6749, 40.6591, 40.6572,
            40.6528, 40.6508, 40.6450, 40.6552, 40.6394, 40.6369,
            40.6323, 40.6279, 40.6258]
})

# Lê os dados do Tracker e remove colunas vazias eventualmente criadas pela vírgula final.
df = pd.read_csv(ARQUIVO_TRACKER, sep=",")
df.columns = [str(c).strip() for c in df.columns]
df = df.loc[:, ~df.columns.str.startswith("Unnamed")]
if "θ" not in df.columns:
    raise ValueError(f"Não encontrei a coluna 'θ'. Colunas lidas: {list(df.columns)}")
df = df.dropna(subset=["t", "θ"]).copy()
df["t"] = pd.to_numeric(df["t"], errors="coerce")
df["θ"] = pd.to_numeric(df["θ"], errors="coerce")
df = df.dropna(subset=["t", "θ"]).sort_values("t")
t = df["t"].to_numpy(float)
theta = df["θ"].to_numpy(float)

# Ângulos interpolados nos tempos manuais; isso não altera os dados originais do Tracker.
angulos = np.interp(tempos_mergulhos, t, theta)
minimos = pd.DataFrame({
    "evento": np.arange(1, len(tempos_mergulhos) + 1),
    "tempo_mergulho_s": tempos_mergulhos,
    "angulo_interpolado_graus": angulos,
})
periodos = np.diff(tempos_mergulhos)
t_medios = (tempos_mergulhos[:-1] + tempos_mergulhos[1:]) / 2
periodos_df = pd.DataFrame({
    "mergulho_inicial": np.arange(1, len(tempos_mergulhos)),
    "mergulho_final": np.arange(2, len(tempos_mergulhos) + 1),
    "t_inicial_s": tempos_mergulhos[:-1],
    "t_final_s": tempos_mergulhos[1:],
    "periodo_s": periodos,
    "tempo_medio_s": t_medios,
})

# Ajuste linear da massa: m(t) = a*t + b
coef = np.polyfit(massa["t_s"], massa["m_g"], 1)
a, b = coef
m_estim = np.polyval(coef, massa["t_s"])
ss_res = np.sum((massa["m_g"] - m_estim) ** 2)
ss_tot = np.sum((massa["m_g"] - massa["m_g"].mean()) ** 2)
r2 = 1 - ss_res / ss_tot if ss_tot else np.nan
taxa_perda_g_s = -a
taxa_perda_g_min = -a * 60
massa_delta = float(massa["m_g"].iloc[-1] - massa["m_g"].iloc[0])

# Estima a massa no ponto médio de cada ciclo por interpolação linear entre leituras próximas.
periodos_df["massa_no_tempo_medio_g"] = np.interp(t_medios, massa["t_s"], massa["m_g"])

# Salva tabelas para rastreabilidade.
massa.to_csv(PASTA / "massa_400_600.csv", index=False)
minimos.to_csv(PASTA / "mergulhadas_400_600.csv", index=False)
periodos_df.to_csv(PASTA / "periodos_e_massa_400_600.csv", index=False)

# 1. Ângulo do Tracker e instantes de mergulho anotados
mask = (t >= INICIO_S) & (t <= FIM_S)
fig, ax = plt.subplots(figsize=(12, 5.5))
ax.plot(t[mask], theta[mask], lw=0.9, label="Ângulo rastreado (Tracker)")
ax.scatter(tempos_mergulhos, angulos, color="red", zorder=3, label="Mergulhadas anotadas")
for i, (tx, ay) in enumerate(zip(tempos_mergulhos, angulos), 1):
    ax.annotate(str(i), (tx, ay), xytext=(0, 7), textcoords="offset points", ha="center", fontsize=8)
ax.set(xlabel="Tempo (s)", ylabel="Ângulo θ (graus)", title=f'Ângulo do Pássaro Bebedor (álcool 70%, H=80%, T=25.4°C): {400}–{600} s')
ax.grid(alpha=0.25); ax.legend(); fig.tight_layout()
fig.savefig(PASTA / "01_angulo_e_mergulhadas.png", dpi=180); plt.close(fig)

# 2. Massa observada e ajuste linear
fig, ax = plt.subplots(figsize=(10, 5.5))
ax.scatter(massa["t_s"], massa["m_g"], label="Massa medida", zorder=3)
t_linha = np.linspace(INICIO_S, FIM_S, 200)
ax.plot(t_linha, np.polyval(coef, t_linha), label=f"Ajuste linear (R² = {r2:.3f})")
ax.set(xlabel="Tempo (s)", ylabel="Massa (g)", title=f'Massa em função do tempo do Pássaro Bebedor (álcool 70%, H=80%, T=25.4°C): {400}–{600} s')
ax.grid(alpha=0.25); ax.legend(); fig.tight_layout()
fig.savefig(PASTA / "02_massa_e_ajuste_linear.png", dpi=180); plt.close(fig)

# 3. Período por tempo médio do ciclo
fig, ax = plt.subplots(figsize=(10, 5.5))
ax.plot(t_medios, periodos, marker="o", label="Período entre mergulhadas")
ax.axhline(periodos.mean(), ls="--", label=f"Média = {periodos.mean():.2f} s")
ax.set(xlabel="Tempo médio do ciclo (s)", ylabel="Período (s)", title=f'Períodos do Pássaro Bebedor (álcool 70%, H=80%, T=25.4°C): {400}–{600} s')
ax.grid(alpha=0.25); ax.legend(); fig.tight_layout()
fig.savefig(PASTA / "03_periodo_ao_longo_do_tempo.png", dpi=180); plt.close(fig)

resumo = f"""ANÁLISE DO PÁSSARO BEBEDOR — INTERVALO {INICIO_S:.0f}–{FIM_S:.0f} s

MASSA
- Número de leituras: {len(massa)}
- Massa inicial medida: {massa['m_g'].iloc[0]:.4f} g
- Massa final medida: {massa['m_g'].iloc[-1]:.4f} g
- Variação observada (final - inicial): {massa_delta:.4f} g
- Inclinação do ajuste linear: {a:.8f} g/s
- Taxa média de perda estimada pelo ajuste: {taxa_perda_g_min:.5f} g/min
- R² do ajuste linear: {r2:.4f}

PERÍODOS ENTRE MERGULHADAS
- Número de mergulhadas anotadas: {len(tempos_mergulhos)}
- Número de intervalos: {len(periodos)}
- Período médio: {periodos.mean():.3f} s
- Desvio-padrão amostral dos períodos: {periodos.std(ddof=1):.3f} s
- Mediana: {np.median(periodos):.3f} s
- Mínimo e máximo: {periodos.min():.3f} a {periodos.max():.3f} s

NOTAS DE INTERPRETAÇÃO
- A reta descreve a tendência geral da massa neste trecho; R² não é a incerteza da balança.
- Oscilações nas leituras de massa foram mantidas como medidas observadas, pois o movimento do pássaro pode afetar a balança.
- A massa nos pontos médios dos ciclos foi estimada por interpolação linear entre leituras.
- O gráfico período × massa é exploratório; nove ciclos não bastam, por si só, para provar causalidade.
"""
(PASTA / "resumo_resultados.txt").write_text(resumo, encoding="utf-8")
print(resumo)

print("Arquivos gerados na pasta:", PASTA)

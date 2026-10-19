"""Análise do passarinho bebedor: mergulhos, períodos e taxa de evaporação.

Instalação: pip install pandas numpy matplotlib scipy

1) Exporte o Tracker para CSV/TXT com colunas t e θ (separador por vírgula).
2) Ajuste ARQUIVO_ANGULO abaixo.
3) Execute. O script salva gráficos por janelas e um gráfico de candidatos a eventos.
4) Confira os candidatos no vídeo e registre os instantes reais dos mergulhos em mergulhos.csv:
       t_mergulho_s
       12.4
       25.1
       ...
   Depois rode novamente; o script calcula os intervalos entre mergulhos anotados.
5) Para massa, crie massa.csv com colunas t_s,m_g e execute a seção indicada.
"""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import find_peaks, savgol_filter

# ---------- CONFIGURAÇÃO ----------
ARQUIVO_ANGULO = Path('alcool70_dia2.txt')
COL_TEMPO = 't'
COL_ANGULO = 'θ'
JANELAS_S = [(0, 600), (0, 200), (200, 400), (400, 600), (600, 700)]
PASTA_SAIDA = Path('visao_geral')
PASTA_SAIDA.mkdir(exist_ok=True)

# Ajuste para detectar candidatos. Isso NÃO substitui conferir o vídeo.
DISTANCIA_MIN_CANDIDATOS_S = 4.0
PROEMINENCIA_GRAUS = 40


def ler_angulo(caminho):
    # O export do Tracker pode ter uma coluna extra vazia no final; ela é ignorada.
    d = pd.read_csv(caminho, sep=',', engine='python')
    d.columns = [str(c).strip() for c in d.columns]
    d = d[[COL_TEMPO, COL_ANGULO]].copy()
    d[COL_TEMPO] = pd.to_numeric(d[COL_TEMPO], errors='coerce')
    d[COL_ANGULO] = pd.to_numeric(d[COL_ANGULO], errors='coerce')
    d = d.dropna().sort_values(COL_TEMPO).drop_duplicates(COL_TEMPO)
    return d


def plotar_janelas(d):
    for ini, fim in JANELAS_S:
        parte = d[(d[COL_TEMPO] >= ini) & (d[COL_TEMPO] < fim)]
        if len(parte) < 2:
            continue
        fig, ax = plt.subplots(figsize=(12, 4.5))
        ax.plot(parte[COL_TEMPO], parte[COL_ANGULO], lw=0.8)
        ax.set(xlabel='Tempo (s)', ylabel='Ângulo θ (graus)',
               title=f'Pássaro Bebedor (álcool 70%, H=80%, T=25.4°C): {ini}–{fim} s')
        ax.grid(True, alpha=.3)
        fig.tight_layout()
        fig.savefig(PASTA_SAIDA / f'angulo_{ini}_{fim}s.png', dpi=180)
        plt.close(fig)


def analisar_mergulhos_manuais():
    caminho = Path('mergulhos.csv')
    if not caminho.exists():
        print('\nPara calcular períodos dos mergulhos, crie mergulhos.csv com uma coluna t_mergulho_s.')
        return
    e = pd.read_csv(caminho)
    tempos = np.sort(pd.to_numeric(e['t_mergulho_s'], errors='coerce').dropna().to_numpy())
    if len(tempos) < 2:
        print('Registre pelo menos dois instantes de mergulho em mergulhos.csv.')
        return
    intervalos = np.diff(tempos)
    res = pd.DataFrame({'mergulho_inicial_s': tempos[:-1],
                        'mergulho_final_s': tempos[1:],
                        'intervalo_s': intervalos,
                        'meio_intervalo_s': (tempos[:-1] + tempos[1:]) / 2})
    res.to_csv(PASTA_SAIDA / 'periodos_mergulhos.csv', index=False)
    print('\nPeríodos entre mergulhos anotados:')
    print(res.to_string(index=False, float_format=lambda x: f'{x:.3f}'))
    print(f"\nN intervalos = {len(intervalos)}; média = {np.mean(intervalos):.3f} s; "
          f"desvio-padrão = {np.std(intervalos, ddof=1) if len(intervalos)>1 else float('nan'):.3f} s")

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(res['meio_intervalo_s'], res['intervalo_s'], 'o-', ms=4)
    ax.set(xlabel='Tempo médio do intervalo (s)', ylabel='Período entre mergulhos (s)',
           title='Variação do período entre mergulhos')
    ax.grid(True, alpha=.3)
    fig.tight_layout()
    fig.savefig(PASTA_SAIDA / 'periodo_mergulhos_ao_longo_do_tempo.png', dpi=180)
    plt.close(fig)


def analisar_massa():
    """Analisa massa.csv (t_s,m_g). Ajuste JANELA_SUAVIZACAO_S à frequência das medidas."""
    caminho = Path('massa.csv')
    if not caminho.exists():
        print('\nPara taxa de evaporação, crie massa.csv com colunas t_s,m_g. Ex.: 0,52.341')
        return
    m = pd.read_csv(caminho).dropna(subset=['t_s', 'm_g']).sort_values('t_s')
    t = pd.to_numeric(m['t_s'], errors='coerce').to_numpy()
    massa = pd.to_numeric(m['m_g'], errors='coerce').to_numpy()
    ok = np.isfinite(t) & np.isfinite(massa)
    t, massa = t[ok], massa[ok]
    if len(t) < 5:
        print('Use pelo menos cinco medidas de massa para estimar uma tendência suavizada.')
        return
    # Interpola para uma malha uniforme e aplica Savitzky–Golay. A janela deve ser
    # escolhida conforme o espaçamento e o ruído; não use janela maior que as mudanças reais.
    dt = np.median(np.diff(t))
    tu = np.arange(t.min(), t.max(), dt)
    mu = np.interp(tu, t, massa)
    janela_s = max(5 * dt, 30.0)  # ponto inicial; ajuste conforme a duração/ruído
    n = int(round(janela_s / dt))
    n = max(5, n if n % 2 else n + 1)
    if n >= len(mu):
        n = len(mu) - 1 if len(mu) % 2 == 0 else len(mu)
    if n < 5:
        print('Há poucos pontos para suavizar a curva de massa.')
        return
    ms = savgol_filter(mu, window_length=n, polyorder=2)
    dmdt = savgol_filter(mu, window_length=n, polyorder=2, deriv=1, delta=dt)
    # Se a massa do conjunto diminui com o tempo, taxa de perda positiva = -dm/dt.
    taxa = -dmdt
    pd.DataFrame({'t_s': tu, 'massa_interp_g': mu, 'massa_suavizada_g': ms,
                  'dm_dt_g_s': dmdt, 'taxa_perda_massa_g_s': taxa}).to_csv(
                      PASTA_SAIDA / 'massa_derivada.csv', index=False)

    fig, ax = plt.subplots(figsize=(10, 4.5))
    ax.plot(t, massa, 'o', ms=3, label='Medidas')
    ax.plot(tu, ms, '-', label='Tendência suavizada')
    ax.set(xlabel='Tempo (s)', ylabel='Massa (g)', title='Massa em função do tempo')
    ax.grid(True, alpha=.3); ax.legend(); fig.tight_layout()
    fig.savefig(PASTA_SAIDA / 'massa_tempo.png', dpi=180); plt.close(fig)

    fig, ax = plt.subplots(figsize=(10, 4.5))
    ax.plot(tu, taxa, '-')
    ax.axhline(0, lw=.8)
    ax.set(xlabel='Tempo (s)', ylabel='Taxa de perda de massa (g/s)',
           title='Taxa estimada de perda de massa: −dm/dt')
    ax.grid(True, alpha=.3); fig.tight_layout()
    fig.savefig(PASTA_SAIDA / 'taxa_evaporacao.png', dpi=180); plt.close(fig)
    print(f'Análise de massa salva em {PASTA_SAIDA.resolve()}.')
    print('Atenção: -dm/dt representa evaporação apenas se outras perdas/ganhos de massa forem desprezíveis.')


if __name__ == '__main__':
    if ARQUIVO_ANGULO.exists():
        dados = ler_angulo(ARQUIVO_ANGULO)
        print(f'{len(dados)} pontos de ângulo; duração {dados[COL_TEMPO].min():.2f}–{dados[COL_TEMPO].max():.2f} s')
        plotar_janelas(dados)
        print(f'Gráficos e candidatos salvos em: {PASTA_SAIDA.resolve()}')
        print('Os extremos automáticos NÃO identificam com certeza as tombadas; confira-os no vídeo.')
    else:
        print(f'Não encontrei {ARQUIVO_ANGULO}. Coloque o arquivo na pasta atual ou ajuste ARQUIVO_ANGULO.')
    analisar_mergulhos_manuais()
    analisar_massa()

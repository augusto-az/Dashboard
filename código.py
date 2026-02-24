
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from datetime import time

# --- CONFIGURAÇÃO E ESTILO ---
st.set_page_config(page_title="Dashboard de Frotas — Cassol", layout="wide")
st.title("Dashboard de Frotas — Cassol Centerlar")
st.markdown('''<style>.block-container{padding-left:4rem;padding-right:4rem;}div[data-testid="stMetric"]{background:#0b3d91;padding:15px;border-radius:12px;color:white;}div[data-testid="stMetric"] label{color:#bbdefb;}</style>''', unsafe_allow_html=True)

# --- FUNÇÕES AUXILIARES ---
def formatar_tempo(td):
    if pd.isna(td): return None
    s = int(td.total_seconds())
    return f"{s//3600:02d}:{(s%3600)//60:02d}:{s%60:02d}"

def abreviar_nome(nome):
    if isinstance(nome, str):
        partes = nome.split()
        if len(partes) > 1:
            return f"{partes[0]} {partes[-1][0].upper()}"
    return nome

def converter_para_timedelta(valor):
    return pd.Timedelta(hours=valor.hour, minutes=valor.minute, seconds=valor.second) if isinstance(valor, time) else pd.NaT

# --- LEITURA E TRATAMENTO ---
df = pd.read_excel("base.xlsx")
df["Nome"] = df["NOME"].apply(abreviar_nome)
df["HORAS LIGADO MOVIMENTO DIA"] = df["HORAS LIGADO MOVIMENTO DIA"].apply(converter_para_timedelta)

# --- MÉTRICAS ---
col_tempo = "HORAS LIGADO MOVIMENTO DIA"
tempo_medio = df[col_tempo].mean()
linha_max = df.loc[df[col_tempo].idxmax()]
linha_min = df.loc[df[col_tempo].idxmin()]
df_excessos = df[df["KM POR DIA PÓS TURNO"] > df["KM CASA-BASE (só ida)"]]
total_motoristas = df["Nome"].nunique()
total_excessos = len(df_excessos)

# --- EXIBIÇÃO DAS MÉTRICAS ---
c1, c2, c3, c4 = st.columns(4)
c1.metric("Tempo Médio", formatar_tempo(tempo_medio))
c2.metric("Tempo Máximo", formatar_tempo(linha_max[col_tempo]))
c3.metric("Motoristas", total_motoristas)
c4.metric("Excessos Pós Turno", total_excessos)
st.divider()

# --- TABELAS ---
df_resumo = pd.DataFrame({
    "Métrica": ["Tempo médio", "Tempo máximo", "Tempo mínimo"],
    "Tempo": [formatar_tempo(tempo_medio), formatar_tempo(linha_max[col_tempo]), formatar_tempo(linha_min[col_tempo])],
    "Nome": ["-", linha_max["Nome"], linha_min["Nome"]],
})
df_excessos = df_excessos.rename(columns={"DIAS PÓS TURNO": "Dias", "KM POR DIA PÓS TURNO": "KM por dia"})[["Nome", "Dias", "KM por dia"]]
df_excessos["KM por dia"] = df_excessos["KM por dia"].round(2)
col_a, col_b = st.columns(2)
with col_a:
    st.subheader("Tempo Ligado em Movimento")
    st.dataframe(df_resumo, use_container_width=True, hide_index=True)
with col_b:
    st.subheader("Excessos Pós Turno")
    st.dataframe(df_excessos, use_container_width=True, hide_index=True)
st.divider()

# --- GRÁFICOS ---
def plot_bar(df, x, y, title, color):
    fig, ax = plt.subplots(figsize=(8, 4.5))
    bars = ax.bar(df[x], df[y], color=color)
    ax.set_title(title)
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
    ax.bar_label(bars, fmt="%.0f", padding=2)
    plt.tight_layout()
    st.pyplot(fig)

df_km_total = df[df["KM TOTAL"] < 10000].sort_values(by="KM TOTAL", ascending=False)
df_km_dnu = df[df["KM DNU"] > 500].sort_values(by="KM DNU", ascending=False)
col_c, col_d = st.columns(2)
with col_c:
    plot_bar(df_km_total, "Nome", "KM TOTAL", "KM Total abaixo de 10.000 km", "#1565c0")
with col_d:
    plot_bar(df_km_dnu, "Nome", "KM DNU", "KM DNU acima de 500 km", "#c62828")

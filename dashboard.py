import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date

st.set_page_config(page_title="Observatório Gestor", layout="wide")

# URL do arquivo CSV no GitHub
CSV_URL = "https://raw.githubusercontent.com/Jocirio/Dashboard-Inovatus/main/Boletim_Diario_dos_Atendimentos.csv"

@st.cache_data(ttl=3600)
def load_data():
    df = pd.read_csv(CSV_URL, encoding="latin-1", on_bad_lines="skip")
    # Faça preprocessamento adicional aqui se quiser
    df.columns = df.columns.str.strip()
    df['Data Atendimento'] = pd.to_datetime(df['Data Atendimento'], errors='coerce')
    df['Idade'] = pd.to_numeric(df['Idade'], errors='coerce')
    bins = [0,5,12,18,30,45,60,150]
    labels = ['0-5','6-12','13-18','19-30','31-45','46-60','60+']
    df['Faixa Etária'] = pd.cut(df['Idade'], bins=bins, labels=labels)
    return df

df = load_data()

# --- Filtros ---
min_date = df['Data Atendimento'].min().date()
max_date = df['Data Atendimento'].max().date()

st.sidebar.header("Filtros")
selected_dates = st.sidebar.date_input(
    "Selecione o intervalo de datas",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
    key='date_filter'
)
if isinstance(selected_dates, tuple):
    selected_start, selected_end = selected_dates
else:
    selected_start = selected_end = selected_dates

unidades = ['Todos'] + sorted(df['Unidade'].dropna().unique())
sexo_opts = ['Todos'] + sorted(df['Sexo'].dropna().unique())
faixa_opts = ['Todos'] + list(df['Faixa Etária'].dropna().unique())
unidade_sel = st.sidebar.selectbox("Unidade", unidades, key='unidade_filter')
sexo_sel = st.sidebar.selectbox("Sexo", sexo_opts, key='sexo_filter')
faixa_sel = st.sidebar.selectbox("Faixa Etária", faixa_opts, key='faixa_filter')

df_filtered = df[
    (df['Data Atendimento'].dt.date >= selected_start) &
    (df['Data Atendimento'].dt.date <= selected_end)
]
if unidade_sel != 'Todos':
    df_filtered = df_filtered[df_filtered['Unidade'] == unidade_sel]
if sexo_sel != 'Todos':
    df_filtered = df_filtered[df_filtered['Sexo'] == sexo_sel]
if faixa_sel != 'Todos':
    df_filtered = df_filtered[df_filtered['Faixa Etária'] == faixa_sel]

# --- Métricas simples ---
total_atend = len(df_filtered)
media_idade = round(df_filtered['Idade'].mean(), 1) if not df_filtered.empty else 0
masc = (df_filtered['Sexo'] == 'Masculino').sum() if not df_filtered.empty else 0
fem = (df_filtered['Sexo'] == 'Feminino').sum() if not df_filtered.empty else 0

col1, col2, col3, col4 = st.columns(4)
col1.markdown(f"<div style='color: green; font-size: 28px; font-weight: bold; text-align:center;'>Total Atendimentos<br>{total_atend}</div>", unsafe_allow_html=True)
col2.markdown(f"<div style='color: orange; font-size: 28px; font-weight: bold; text-align:center;'>Média Idade<br>{media_idade}</div>", unsafe_allow_html=True)
col3.markdown(f"<div style='color: blue; font-size: 28px; font-weight: bold; text-align:center;'>Masculino<br>{masc}</div>", unsafe_allow_html=True)
col4.markdown(f"<div style='color: pink; font-size: 28px; font-weight: bold; text-align:center;'>Feminino<br>{fem}</div>", unsafe_allow_html=True)

# --- Gráficos ---
st.markdown("<h2 style='text-align:center;'>Atendimentos por Unidade</h2>", unsafe_allow_html=True)
uni_dist = df_filtered['Unidade'].value_counts().reset_index()
uni_dist.columns = ['Unidade', 'Quantidade']
fig_uni = px.bar(uni_dist, x='Unidade', y='Quantidade')
st.plotly_chart(fig_uni, use_container_width=True)

st.markdown("<h2 style='text-align:center;'>Distribuição por Sexo</h2>", unsafe_allow_html=True)
sexo_dist = df_filtered['Sexo'].value_counts().reset_index()
sexo_dist.columns = ['Sexo', 'Quantidade']
st.plotly_chart(px.pie(sexo_dist, names='Sexo', values='Quantidade'), use_container_width=True)

# Continue ajustando e acrescentando conforme seu dashboard original utiliza o df_filtered


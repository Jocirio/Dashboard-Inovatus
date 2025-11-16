import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Observatório Gestor", layout="wide")

# Link direto do CSV público no GitHub
CSV_URL = "https://raw.githubusercontent.com/Jocirio/Dashboard-Inovatus/main/Boletim_Diario_dos_Atendimentos.csv"

@st.cache_data(ttl=3600)
def load_data():
    df = pd.read_csv(CSV_URL, encoding='latin-1', on_bad_lines='skip')
    df.columns = df.columns.str.strip()
    df['Data Atendimento'] = pd.to_datetime(df['Data Atendimento'], errors='coerce')
    df['Idade'] = pd.to_numeric(df['Idade'], errors='coerce')
    bins = [0,5,12,18,30,45,60,150]
    labels = ['0-5','6-12','13-18','19-30','31-45','46-60','60+']
    df['Faixa Etária'] = pd.cut(df['Idade'], bins=bins, labels=labels)
    return df

df = load_data()

# Filtros Sidebar
min_date = df['Data Atendimento'].min().date()
max_date = df['Data Atendimento'].max().date()

st.sidebar.header("Filtros")
date_input = st.sidebar.date_input("Intervalo de Datas", [min_date, max_date], min_value=min_date, max_value=max_date)
unidades = ['Todos'] + sorted(df['Unidade'].dropna().unique())
sexo = ['Todos'] + sorted(df['Sexo'].dropna().unique())
faixas = ['Todos'] + list(df['Faixa Etária'].dropna().unique())

unidade_sel = st.sidebar.selectbox("Unidade", unidades)
sexo_sel = st.sidebar.selectbox("Sexo", sexo)
faixa_sel = st.sidebar.selectbox("Faixa Etária", faixas)

# Aplica os filtros
df_filtered = df[
    (df['Data Atendimento'].dt.date >= date_input[0]) & 
    (df['Data Atendimento'].dt.date <= date_input[1])
]

if unidade_sel != "Todos":
    df_filtered = df_filtered[df_filtered['Unidade'] == unidade_sel]
if sexo_sel != "Todos":
    df_filtered = df_filtered[df_filtered['Sexo'] == sexo_sel]
if faixa_sel != "Todos":
    df_filtered = df_filtered[df_filtered['Faixa Etária'] == faixa_sel]

# Título e métricas
st.title("Observatório Gestor")
col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Atendimentos", len(df_filtered))
col2.metric("Média de Idade", round(df_filtered['Idade'].mean(), 1) if len(df_filtered) > 0 else 0)
col3.metric("Masculino", (df_filtered['Sexo'] == 'Masculino').sum() if len(df_filtered) > 0 else 0)
col4.metric("Feminino", (df_filtered['Sexo'] == 'Feminino').sum() if len(df_filtered) > 0 else 0)

# Gráficos
st.header("Atendimentos por Unidade")
uni_counts = df_filtered['Unidade'].value_counts().reset_index()
uni_counts.columns = ['Unidade', 'Quantidade']
fig1 = px.bar(uni_counts, x='Unidade', y='Quantidade')
st.plotly_chart(fig1, use_container_width=True)

st.header("Distribuição por Sexo")
sex_counts = df_filtered['Sexo'].value_counts().reset_index()
sex_counts.columns = ['Sexo', 'Quantidade']
fig2 = px.pie(sex_counts, names='Sexo', values='Quantidade')
st.plotly_chart(fig2, use_container_width=True)

st.header("Distribuição por Faixa Etária")
faixa_counts = df_filtered['Faixa Etária'].value_counts().reset_index()
faixa_counts.columns = ['Faixa Etária', 'Quantidade']
fig3 = px.bar(faixa_counts, x='Faixa Etária', y='Quantidade')
st.plotly_chart(fig3, use_container_width=True)

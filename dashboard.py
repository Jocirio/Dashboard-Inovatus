import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Observatório Gestor", layout="wide")

# Link para o CSV no seu GitHub - ajuste conforme o caminho correto
CSV_URL = "https://raw.githubusercontent.com/Jocirio/Dashboard-Inovatus/main/Boletim_Diario_dos_Atendimentos.csv"

@st.cache_data(ttl=3600)
def load_data():
    df = pd.read_csv(CSV_URL, encoding="latin-1", on_bad_lines="skip")
    df.columns = df.columns.str.strip()
    df['Data Atendimento'] = pd.to_datetime(df['Data Atendimento'], errors='coerce')
    df['Idade'] = pd.to_numeric(df['Idade'], errors='coerce')
    bins = [0,5,12,18,30,45,60,150]
    labels = ['0-5','6-12','13-18','19-30','31-45','46-60','60+']
    df['Faixa Etária'] = pd.cut(df['Idade'], bins=bins, labels=labels)
    return df

df = load_data()

min_date = df['Data Atendimento'].min().date()
max_date = df['Data Atendimento'].max().date()

# Sidebar com filtros
st.sidebar.header("Filtros")
date_filter = st.sidebar.date_input("Intervalo de datas", [min_date, max_date], min_value=min_date, max_value=max_date)

unidades = ['Todos'] + sorted(df['Unidade'].dropna().unique())
sexo_opts = ['Todos'] + sorted(df['Sexo'].dropna().unique())
faixa_opts = ['Todos'] + list(df['Faixa Etária'].dropna().unique())

unidade_sel = st.sidebar.selectbox("Unidade", unidades)
sexo_sel = st.sidebar.selectbox("Sexo", sexo_opts)
faixa_sel = st.sidebar.selectbox("Faixa Etária", faixa_opts)

# Aplicar filtros
df_filtered = df[
    (df['Data Atendimento'].dt.date >= date_filter[0]) & 
    (df['Data Atendimento'].dt.date <= date_filter[1])
]

if unidade_sel != "Todos":
    df_filtered = df_filtered[df_filtered['Unidade'] == unidade_sel]

if sexo_sel != "Todos":
    df_filtered = df_filtered[df_filtered['Sexo'] == sexo_sel]

if faixa_sel != "Todos":
    df_filtered = df_filtered[df_filtered['Faixa Etária'] == faixa_sel]

# Métricas
st.title("Observatório Gestor")

total_atend = len(df_filtered)
media_idade = round(df_filtered['Idade'].mean(), 1) if not df_filtered.empty else 0
masc = (df_filtered['Sexo'] == 'Masculino').sum() if not df_filtered.empty else 0
fem = (df_filtered['Sexo'] == 'Feminino').sum() if not df_filtered.empty else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Atendimentos", total_atend)
col2.metric("Média de Idade", media_idade)
col3.metric("Masculino", masc)
col4.metric("Feminino", fem)

# Gráficos
st.header("Atendimentos por Unidade")
df_uni = df_filtered['Unidade'].value_counts().reset_index()
df_uni.columns = ['Unidade', 'Quantidade']
fig_uni = px.bar(df_uni, x='Unidade', y='Quantidade', title="Atendimentos por Unidade")
st.plotly_chart(fig_uni, use_container_width=True)

st.header("Distribuição por Sexo")
df_sexo = df_filtered['Sexo'].value_counts().reset_index()
df_sexo.columns = ['Sexo', 'Quantidade']
fig_sexo = px.pie(df_sexo, names='Sexo', values='Quantidade', title="Distribuição por Sexo")
st.plotly_chart(fig_sexo, use_container_width=True)

st.header("Distribuição por Faixa Etária")
df_faixa = df_filtered['Faixa Etária'].value_counts().reset_index()
df_faixa.columns = ['Faixa Etária', 'Quantidade']
fig_faixa = px.bar(df_faixa, x='Faixa Etária', y='Quantidade', title="Distribuição por Faixa Etária")
st.plotly_chart(fig_faixa, use_container_width=True)

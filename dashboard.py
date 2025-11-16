import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date

st.set_page_config(page_title="Observatório Gestor", layout="wide")

# URL CSV no GitHub
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

st.sidebar.header("Filtros")

date_range = st.sidebar.date_input("Intervalo de Datas",
                                   value=(min_date, max_date),
                                   min_value=min_date, max_value=max_date)
unit_options = ['Todos'] + sorted(df['Unidade'].dropna().unique())
sex_options = ['Todos'] + sorted(df['Sexo'].dropna().unique())
age_options = ['Todos'] + list(df['Faixa Etária'].dropna().unique())
proc_options = ['Todos'] + sorted(df['Procedimento'].dropna().unique())
prof_options = ['Todos'] + sorted(df['Profissional'].dropna().unique())

unit_selected = st.sidebar.selectbox("Unidade", unit_options)
sex_selected = st.sidebar.selectbox("Sexo", sex_options)
age_selected = st.sidebar.selectbox("Faixa Etária", age_options)
proc_selected = st.sidebar.selectbox("Filtro Procedimentos", proc_options)
prof_selected = st.sidebar.selectbox("Filtro Profissionais", prof_options)
top_n_proc = st.sidebar.selectbox("Top N Procedimentos", [10, 20, 30, 'Todos'], index=0)
top_n_prof = st.sidebar.selectbox("Top N Profissionais", [10, 20, 30, 'Todos'], index=0)

if isinstance(date_range, tuple):
    start_date, end_date = date_range
else:
    start_date = end_date = date_range

df_filtered = df[
    (df['Data Atendimento'].dt.date >= start_date) & (df['Data Atendimento'].dt.date <= end_date)
]

if unit_selected != 'Todos':
    df_filtered = df_filtered[df_filtered['Unidade'] == unit_selected]
if sex_selected != 'Todos':
    df_filtered = df_filtered[df_filtered['Sexo'] == sex_selected]
if age_selected != 'Todos':
    df_filtered = df_filtered[df_filtered['Faixa Etária'] == age_selected]
if proc_selected != 'Todos':
    df_filtered = df_filtered[df_filtered['Procedimento'] == proc_selected]
if prof_selected != 'Todos':
    df_filtered = df_filtered[df_filtered['Profissional'] == prof_selected]

# Métricas coloridas (exemplo simples)
def metric_color(value, positive=True):
    if positive:
        color = "green" if value > 0 else "red"
    else:
        color = "red" if value > 0 else "green"
    return f'<span style="color:{color};font-weight:bold">{value}</span>'

total_atend = len(df_filtered)
media_idade = round(df_filtered['Idade'].mean(), 1) if total_atend > 0 else 0
masc = (df_filtered['Sexo'] == 'Masculino').sum() if total_atend > 0 else 0
fem = (df_filtered['Sexo'] == 'Feminino').sum() if total_atend > 0 else 0

st.markdown(
    f"""
    <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:20px;">
        <h1 style="margin:0">Observatório Gestor</h1>
        <!-- Logo aqui, ajuste URL para sua imagem -->
        <img src="https://raw.githubusercontent.com/Jocirio/Dashboard-Inovatus/main/logo.png" alt="Logo" style="height:60px;">
    </div>
    """,
    unsafe_allow_html=True
)

cols = st.columns(4)
cols[0].markdown(f"Total Atendimentos<br>{metric_color(total_atend)}", unsafe_allow_html=True)
cols[1].markdown(f"Média de Idade<br>{metric_color(media_idade)}", unsafe_allow_html=True)
cols[2].markdown(f"Masculino<br>{metric_color(masc)}", unsafe_allow_html=True)
cols[3].markdown(f"Feminino<br>{metric_color(fem)}", unsafe_allow_html=True)

# Gráficos lado a lado
left_col, right_col = st.columns(2)

with left_col:
    st.header("Atendimentos por Unidade")
    df_unidade = df_filtered['Unidade'].value_counts().reset_index()
    df_unidade.columns = ['Unidade', 'Quantidade']
    fig_uni = px.bar(df_unidade, x='Unidade', y='Quantidade')
    st.plotly_chart(fig_uni, use_container_width=True)

    st.header(f"Top {top_n_proc} Procedimentos")
    top_procs = df_filtered['Procedimento'].value_counts().head(top_n_proc if top_n_proc != 'Todos' else None)
    fig_procs = px.bar(top_procs, x=top_procs.index, y=top_procs.values,
                       labels={'x':'Procedimento', 'y':'Quantidade'})
    st.plotly_chart(fig_procs, use_container_width=True)

with right_col:
    st.header("Distribuição por Sexo")
    df_sexo = df_filtered['Sexo'].value_counts().reset_index()
    df_sexo.columns = ['Sexo', 'Quantidade']
    fig_sexo = px.pie(df_sexo, names='Sexo', values='Quantidade')
    st.plotly_chart(fig_sexo, use_container_width=True)

    st.header(f"Top {top_n_prof} Profissionais")
    top_profs = df_filtered['Profissional'].value_counts().head(top_n_prof if top_n_prof != 'Todos' else None)
    fig_profs = px.bar(top_profs, x=top_profs.index, y=top_profs.values,
                       labels={'x':'Profissional', 'y':'Quantidade'})
    st.plotly_chart(fig_profs, use_container_width=True)

st.header("Distribuição por Faixa Etária")
df_faixa = df_filtered['Faixa Etária'].value_counts().reset_index()
df_faixa.columns = ['Faixa Etária', 'Quantidade']
fig_faixa = px.bar(df_faixa, x='Faixa Etária', y='Quantidade')
st.plotly_chart(fig_faixa, use_container_width=True)

st.header("Procedimentos por Faixa Etária")
fig_scatter = px.scatter(df_filtered, x='Faixa Etária', y='Procedimento',
                         size='Idade', color='Sexo',
                         labels={'Faixa Etária':'Faixa Etária', 'Procedimento':'Procedimento'},
                         title='Procedimentos x Faixa Etária')
st.plotly_chart(fig_scatter, use_container_width=True)

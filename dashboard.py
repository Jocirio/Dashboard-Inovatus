import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Observatório Gestor", layout="wide")

# Lista de URLs para os arquivos CSV públicos (GitHub ou Google Drive links públicos)
CSV_URLS = [
    # Exemplo de URL do Google Drive público no formato download direto
    "https://drive.google.com/uc?export=download&id=ID_DO_ARQUIVO_1",
    "https://drive.google.com/uc?export=download&id=ID_DO_ARQUIVO_2",
    # Adicione mais URLs públicas conforme necessário
]

@st.cache_data(ttl=3600)
def load_data():
    dfs = []
    for url in CSV_URLS:
        dfs.append(pd.read_csv(url, encoding="latin-1", on_bad_lines="skip"))
    df = pd.concat(dfs, ignore_index=True)
    df.columns = df.columns.str.strip()
    df['Data Atendimento'] = pd.to_datetime(df['Data Atendimento'], errors='coerce')
    df['Idade'] = pd.to_numeric(df['Idade'], errors='coerce')
    bins = [0, 5, 12, 18, 30, 45, 60, 150]
    labels_ordered = ['0-5', '6-12', '13-18', '19-30', '31-45', '46-60', '60+']
    df['Faixa Etária'] = pd.cut(df['Idade'], bins=bins, labels=labels_ordered, ordered=True)
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
age_options = ['Todos'] + list(pd.Categorical(df['Faixa Etária'], categories=labels_ordered, ordered=True).dropna().unique())
proc_options = ['Todos'] + sorted(df['Procedimento'].dropna().unique())
prof_options = ['Todos'] + sorted(df['Profissional'].dropna().unique())

unit_selected = st.sidebar.selectbox("Unidade", unit_options)
sex_selected = st.sidebar.selectbox("SEXO", sex_options)
age_selected = st.sidebar.selectbox("Faixa Etária", age_options)
proc_selected = st.sidebar.selectbox("Filtro Procedimentos", proc_options)
prof_selected = st.sidebar.selectbox("Filtro Profissionais", prof_options)
top_n_proc = st.sidebar.selectbox("Top N Procedimentos", [10, 20, 30, 'Todos'], index=0)
top_n_prof = st.sidebar.selectbox("Top N Profissionais", [10, 20, 30, 'Todos'], index=0)

if isinstance(date_range, tuple):
    start_date, end_date = date_range
else:
    start_date = end_date = date_range

df_filtered = df[(df['Data Atendimento'].dt.date >= start_date) & (df['Data Atendimento'].dt.date <= end_date)]

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

def card_metric(title, value):
    return f"""
    <div style='background-color:#4CAF50; border-radius:8px; padding:20px; text-align:center; color:white; min-width:170px;'>
        <h3 style='margin:5px'>{title}</h3>
        <p style='font-size:30px; font-weight:bold; margin:0'>{value}</p>
    </div>
    """

col1, col2, col3, col4 = st.columns(4)
col1.markdown(card_metric("Total Atendimentos", 9633), unsafe_allow_html=True)
col2.markdown(card_metric("Média de Idade", 34.5), unsafe_allow_html=True)
col3.markdown(card_metric("Masculino", 4191), unsafe_allow_html=True)
col4.markdown(card_metric("Feminino", 5442), unsafe_allow_html=True)

st.markdown("""
<div style='display:flex; align-items:center; justify-content:center; margin:20px 0'>
    <h1 style='text-align:center; margin:0'>Observatório Gestor</h1>
    <img src='https://raw.githubusercontent.com/seu_usuario/seu_repositorio/main/logo.png' alt='Logo' style='height:70px; margin-left:15px;'>
</div>
""", unsafe_allow_html=True)

left_col, right_col = st.columns(2)

with left_col:
    st.markdown("<h2 style='text-align:center;'>Atendimentos por Unidade</h2>", unsafe_allow_html=True)
    df_unidade = df_filtered['Unidade'].value_counts().reset_index()
    df_unidade.columns = ['Unidade', 'Quantidade']
    fig_uni = px.bar(df_unidade, x='Unidade', y='Quantidade')
    st.plotly_chart(fig_uni, use_container_width=True)

    st.markdown(f"<h2 style='text-align:center;'>Top {top_n_proc} Procedimentos</h2>", unsafe_allow_html=True)
    top_procs = df_filtered['Procedimento'].value_counts().head(top_n_proc if top_n_proc != 'Todos' else None)
    fig_procs = px.bar(top_procs, x=top_procs.index, y=top_procs.values,
                       labels={'x':'Procedimento', 'y':'Quantidade'})
    st.plotly_chart(fig_procs, use_container_width=True)

with right_col:
    st.markdown("<h2 style='text-align:center;'>SEXO</h2>", unsafe_allow_html=True)
    df_sexo = df_filtered['Sexo'].value_counts().reset_index()
    df_sexo.columns = ['Sexo', 'Quantidade']
    fig_sexo = px.pie(df_sexo, names='Sexo', values='Quantidade')
    st.plotly_chart(fig_sexo, use_container_width=True)

    st.markdown(f"<h2 style='text-align:center;'>Top {top_n_prof} Profissionais</h2>", unsafe_allow_html=True)
    top_profs = df_filtered['Profissional'].value_counts().head(top_n_prof if top_n_prof != 'Todos' else None)
    fig_profs = px.bar(top_profs, x=top_profs.index, y=top_profs.values,
                       labels={'x':'Profissional', 'y':'Quantidade'})
    st.plotly_chart(fig_profs, use_container_width=True)

st.markdown("<h2 style='text-align:center;'>Faixa Etária</h2>", unsafe_allow_html=True)
df_faixa = df_filtered['Faixa Etária'].value_counts().reindex(labels_ordered).reset_index()
df_faixa.columns = ['Faixa Etária', 'Quantidade']
fig_faixa = px.bar(df_faixa, x='Faixa Etária', y='Quantidade')
st.plotly_chart(fig_faixa, use_container_width=True)

st.markdown("<h2 style='text-align:center;'>Procedimentos por Faixa Etária</h2>", unsafe_allow_html=True)
fig_scatter = px.scatter(df_filtered, x='Faixa Etária', y='Procedimento',
                         size='Idade', color='Sexo',
                         labels={'Faixa Etária':'Faixa Etária', 'Procedimento':'Procedimento'},
                         title='')
st.plotly_chart(fig_scatter, use_container_width=True)

st.markdown("<h2 style='text-align:center;'>Dados Filtrados</h2>", unsafe_allow_html=True)
st.dataframe(df_filtered)

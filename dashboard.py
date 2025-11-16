import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date
from google.oauth2 import service_account
from googleapiclient.discovery import build
import io
import requests

st.set_page_config(page_title="Observatório Gestor", layout="wide")

# --- Autenticação admin ---
if "admin" not in st.session_state:
    st.session_state["admin"] = False
if not st.session_state["admin"]:
    user = st.sidebar.text_input("Usuário")
    senha = st.sidebar.text_input("Senha", type="password")
    if st.sidebar.button("Entrar"):
        if user == "admin" and senha == "Inova25":
            st.session_state["admin"] = True
            st.sidebar.success("Admin autenticado! Atualize a página para continuar.")
else:
    st.sidebar.success("Área administrativa liberada")
    uploaded_files = st.sidebar.file_uploader(
        "Carregue arquivos CSV", type=["csv"], accept_multiple_files=True
    )
    logo_file = st.sidebar.file_uploader(
        "Upload da logo", type=["png", "jpg", "jpeg"]
    )
    if uploaded_files:
        dfs = [pd.read_csv(f, encoding="latin-1", on_bad_lines="skip") for f in uploaded_files]
        df = pd.concat(dfs, ignore_index=True)
        st.session_state["df"] = df
        st.session_state["logo"] = logo_file

df = st.session_state.get("df", None)
logo_file = st.session_state.get("logo", None)

if df is None:
    st.warning("Aguardando upload pelo administrador.")
    st.stop()

df.columns = df.columns.str.strip()
df['Data Atendimento'] = pd.to_datetime(df['Data Atendimento'], errors='coerce')
df['Idade'] = pd.to_numeric(df['Idade'], errors='coerce')

bins = [0,5,12,18,30,45,60,150]
labels = ['0-5','6-12','13-18','19-30','31-45','46-60','60+']
df['Faixa Etária'] = pd.cut(df['Idade'], bins=bins, labels=labels)

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
proc_opts = ['Todos'] + sorted(df['Procedimento'].dropna().unique())
prof_opts = ['Todos'] + sorted(df['Profissional'].dropna().unique())

unidade_sel = st.sidebar.selectbox("Unidade", unidades, key='unidade_filter')
sexo_sel = st.sidebar.selectbox("Sexo", sexo_opts, key='sexo_filter')
faixa_sel = st.sidebar.selectbox("Faixa Etária", faixa_opts, key='faixa_filter')
proc_sel = st.sidebar.selectbox("Filtro Procedimentos", proc_opts, key='procedimento_filter')
prof_sel = st.sidebar.selectbox("Filtro Profissionais", prof_opts, key='profissional_filter')
top_n_proc = st.sidebar.selectbox("Filtro Procedimentos", [10, 20, 30, 'Todos'], index=0, key='top_n_proc')
top_n_prof = st.sidebar.selectbox("Filtro Profissionais", [10, 20, 30, 'Todos'], index=0, key='top_n_prof')

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
if proc_sel != 'Todos':
    df_filtered = df_filtered[df_filtered['Procedimento'] == proc_sel]
if prof_sel != 'Todos':
    df_filtered = df_filtered[df_filtered['Profissional'] == prof_sel]

all_procs = df['Procedimento'].dropna().unique()
if top_n_proc == 'Todos':
    top_proc_list = all_procs
    num_proc = len(top_proc_list)
else:
    freq_proc = df_filtered['Procedimento'].value_counts().index.tolist()
    top_proc_list = freq_proc[:int(top_n_proc)]
    if len(top_proc_list) < int(top_n_proc):
        missing = [p for p in all_procs if p not in top_proc_list]
        top_proc_list = top_proc_list + missing[:int(top_n_proc) - len(top_proc_list)]
    num_proc = len(top_proc_list)

proc_counts_full = df_filtered['Procedimento'].value_counts()
proc_display = pd.Series(0, index=top_proc_list)
for proc, qtd in proc_counts_full.items():
    if proc in proc_display.index:
        proc_display[proc] = qtd
proc_display = proc_display.reset_index()
proc_display.columns = ['Procedimento', 'Quantidade']

cols = st.columns([8, 1])
cols[0].markdown("<h1 style='text-align:center;'>Observatório Gestor</h1>", unsafe_allow_html=True)
if logo_file:
    cols[1].image(logo_file, use_container_width=True)

total_atend = len(df_filtered)
media_idade = round(df_filtered['Idade'].mean(), 1) if not df_filtered.empty else 0
masc = (df_filtered['Sexo'] == 'Masculino').sum() if not df_filtered.empty else 0
fem = (df_filtered['Sexo'] == 'Feminino').sum() if not df_filtered.empty else 0

col1, col2, col3, col4 = st.columns(4)
col1.markdown(f"<div style='color: green; font-size: 28px; font-weight: bold; text-align:center;'>Total Atendimentos<br>{total_atend}</div>", unsafe_allow_html=True)
col2.markdown(f"<div style='color: orange; font-size: 28px; font-weight: bold; text-align:center;'>Média Idade<br>{media_idade}</div>", unsafe_allow_html=True)
col3.markdown(f"<div style='color: blue; font-size: 28px; font-weight: bold; text-align:center;'>Masculino<br>{masc}</div>", unsafe_allow_html=True)
col4.markdown(f"<div style='color: pink; font-size: 28px; font-weight: bold; text-align:center;'>Feminino<br>{fem}</div>", unsafe_allow_html=True)

col_a, col_b = st.columns(2)
with col_a:
    st.markdown("<h2 style='text-align:center;'>Profissionais</h2>", unsafe_allow_html=True)
    st.subheader(f"Filtro Profissionais: Top {top_n_prof}")
    top_prof = df_filtered['Profissional'].value_counts()
    if top_n_prof == 'Todos':
        num_prof = len(top_prof)
    else:
        num_prof = int(top_n_prof)
    top_prof = top_prof.head(num_prof).reset_index()
    top_prof.columns = ['Profissional', 'Quantidade']
    fig_prof = px.bar(top_prof, x='Profissional', y='Quantidade', title='Profissionais')
    st.plotly_chart(fig_prof, use_container_width=True)
with col_b:
    st.markdown("<h2 style='text-align:center;'>SEXO</h2>", unsafe_allow_html=True)
    sexo_dist = df_filtered['Sexo'].value_counts().reset_index()
    sexo_dist.columns = ['Sexo', 'Quantidade']
    st.plotly_chart(
        px.pie(sexo_dist, names="Sexo", values="Quantidade"), use_container_width=True
    )

col_c, col_d = st.columns(2)
with col_c:
    st.markdown("<h2 style='text-align:center;'>Faixa Etária</h2>", unsafe_allow_html=True)
    faixa_dist = df_filtered['Faixa Etária'].value_counts().reset_index()
    faixa_dist.columns = ['Faixa Etária', 'Quantidade']
    faixa_dist = faixa_dist.sort_values('Faixa Etária')
    fig_faixa = px.bar(faixa_dist, x='Faixa Etária', y='Quantidade')
    st.plotly_chart(fig_faixa, use_container_width=True)
with col_d:
    st.markdown("<h2 style='text-align:center;'>Atendimentos por Unidade</h2>", unsafe_allow_html=True)
    uni_dist = df_filtered['Unidade'].value_counts().reset_index()
    uni_dist.columns = ['Unidade', 'Quantidade']
    fig_uni = px.bar(uni_dist, x='Unidade', y='Quantidade')
    st.plotly_chart(fig_uni, use_container_width=True)

st.markdown("<h2 style='text-align:center;'>Procedimentos x Faixa Etária</h2>", unsafe_allow_html=True)
proc_faixa = df_filtered.groupby(['Procedimento', 'Faixa Etária']).size().reset_index(name='Quantidade')
fig_scatter = px.scatter(proc_faixa, x='Faixa Etária', y='Procedimento', size='Quantidade', color='Quantidade', title='Distribuição de Procedimentos por Faixa Etária', size_max=30)
st.plotly_chart(fig_scatter, use_container_width=True)

if st.session_state.get('selected_procedure') is None:
    fig_proc = px.bar(proc_display, x='Procedimento', y='Quantidade', title=f'Top {num_proc} Procedimentos')
    st.plotly_chart(fig_proc, use_container_width=True)
    proc_click = st.selectbox("Clique para detalhar procedimento", options=[''] + proc_display['Procedimento'].tolist())
    if proc_click:
        st.session_state['selected_procedure'] = proc_click
else:
    st.subheader(f"Detalhes do Procedimento: {st.session_state['selected_procedure']}")
    df_proc = df_filtered[df_filtered['Procedimento'] == st.session_state['selected_procedure']]
    prof_counts = df_proc['Profissional'].value_counts().reset_index()
    prof_counts.columns = ['Profissional', 'Quantidade']
    fig_prof_detail = px.bar(prof_counts, x='Profissional', y='Quantidade', title=f"Profissionais que realizaram {st.session_state['selected_procedure']}")
    st.plotly_chart(fig_prof_detail, use_container_width=True)
    if st.button("Voltar"):
        st.session_state['selected_procedure'] = None

st.markdown("<h2 style='text-align:center;'>Tabela de Dados Filtrados</h2>", unsafe_allow_html=True)
st.dataframe(df_filtered)

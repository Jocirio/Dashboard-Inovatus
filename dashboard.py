import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date

st.set_page_config(page_title="Observatório Gestor", layout="wide")

# Autenticação de administrador
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
            st.sidebar.error("Usuário ou senha incorretos")
    st.stop()
else:
    st.sidebar.success("Área administrativa liberada")

# Upload de arquivos CSV e logo pelo administrador
uploaded_files = st.sidebar.file_uploader("Carregue arquivos CSV", type=["csv"], accept_multiple_files=True)
logo_file = st.sidebar.file_uploader("Upload da logo", type=["png", "jpg", "jpeg"])

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

# Pré-processamento
df.columns = df.columns.str.strip()
df['Data Atendimento'] = pd.to_datetime(df['Data Atendimento'], errors='coerce')
df['Idade'] = pd.to_numeric(df['Idade'], errors='coerce')
bins = [0,5,12,18,30,45,60,150]
labels = ['0-5','6-12','13-18','19-30','31-45','46-60','60+']
df['Faixa Etária'] = pd.cut(df['Idade'], bins=bins, labels=labels)

# Filtros Sidebar
min_date = df['Data Atendimento'].min().date()
max_date = df['Data Atendimento'].max().date()

st.sidebar.header("Filtros")

date_range = st.sidebar.date_input("Intervalo de Datas", [min_date, max_date], min_value=min_date, max_value=max_date)
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

# Aplicação dos filtros
if isinstance(date_range, tuple):
    start_date, end_date = date_range
else:
    start_date = end_date = date_range

df_filtered = df[
    (df['Data Atendimento'].dt.date >= start_date) & 
    (df['Data Atendimento'].dt.date <= end_date)
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

# Top N procedimentos
all_procs = df['Procedimento'].dropna().unique()
if top_n_proc == 'Todos':
    top_proc_list = all_procs
else:
    freq_proc = df_filtered['Procedimento'].value_counts().index.tolist()
    top_proc_list = freq_proc[:int(top_n_proc)]
    if len(top_proc_list) < int(top_n_proc):
        missing = [p for p in all_procs if p not in top_proc_list]
        top_proc_list += missing[:int(top_n_proc) - len(top_proc_list)]

proc_counts_full = df_filtered['Procedimento'].value_counts()
proc_display = pd.Series(0, index=top_proc_list)
for proc, qtd in proc_counts_full.items():
    if proc in proc_display.index:
        proc_display[proc] = qtd
proc_display = proc_display.reset_index()
proc_display.columns = ['Procedimento', 'Quantidade']

# Top N profissionais
all_profs = df['Profissional'].dropna().unique()
if top_n_prof == 'Todos':
    top_prof_list = all_profs
else:
    freq_prof = df_filtered['Profissional'].value_counts().index.tolist()
    top_prof_list = freq_prof[:int(top_n_prof)]
    if len(top_prof_list) < int(top_n_prof):
        missing = [p for p in all_profs if p not in top_prof_list]
        top_prof_list += missing[:int(top_n_prof) - len(top_prof_list)]

prof_counts_full = df_filtered['Profissional'].value_counts()
prof_display = pd.Series(0, index=top_prof_list)
for prof, qtd in prof_counts_full.items():
    if prof in prof_display.index:
        prof_display[prof] = qtd
prof_display = prof_display.reset_index()
prof_display.columns = ['Profissional', 'Quantidade']

# Métricas gerais
st.title("Observatório Gestor")

col1, col2, col3, col4, col5, col6 = st.columns(6)

col1.metric("Total Atendimentos", len(df_filtered))
col2.metric("Média de Idade", round(df_filtered['Idade'].mean(), 1) if not df_filtered.empty else 0)
col3.metric("Masculino", (df_filtered['Sexo'] == 'Masculino').sum() if not df_filtered.empty else 0)
col4.metric("Feminino", (df_filtered['Sexo'] == 'Feminino').sum() if not df_filtered.empty else 0)
col5.metric("Total Procedimentos", len(proc_display))
col6.metric("Total Profissionais", len(prof_display))

# Gráficos
st.header("Atendimentos por Unidade")
df_uni = df_filtered['Unidade'].value_counts().reset_index()
df_uni.columns = ['Unidade', 'Quantidade']
fig_uni = px.bar(df_uni, x='Unidade', y='Quantidade')
st.plotly_chart(fig_uni, use_container_width=True)

st.header("Distribuição por Sexo")
df_sexo = df_filtered['Sexo'].value_counts().reset_index()
df_sexo.columns = ['Sexo', 'Quantidade']
fig_sexo = px.pie(df_sexo, names='Sexo', values='Quantidade')
st.plotly_chart(fig_sexo, use_container_width=True)

st.header("Distribuição por Faixa Etária")
df_faixa = df_filtered['Faixa Etária'].value_counts().reset_index()
df_faixa.columns = ['Faixa Etária', 'Quantidade']
fig_faixa = px.bar(df_faixa, x='Faixa Etária', y='Quantidade')
st.plotly_chart(fig_faixa, use_container_width=True)

st.header(f"Top {top_n_proc} Procedimentos")
st.dataframe(proc_display)

st.header(f"Top {top_n_prof} Profissionais")
st.dataframe(prof_display)

# Exibir logo
if logo_file:
    st.sidebar.image(logo_file, width=200)

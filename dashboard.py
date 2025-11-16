import pandas as pd
import plotly.express as px
from google.oauth2 import service_account
from googleapiclient.discovery import build
import io
import requests

st.set_page_config(page_title="Observatório Gestor", layout="wide")

FOLDER_ID = "1HCbC3HMy-a-ObPtOnDzsyHdLuH5pGbSb"
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

@st.cache_data(ttl=3600)
def load_data():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('drive', 'v3', credentials=creds)
    results = service.files().list(
        q=f"'{FOLDER_ID}' in parents and mimeType='text/csv'",
        fields="files(id, name)").execute()
    items = results.get('files', [])
    
    dfs = []
    for item in items:
        file_id = item['id']
        download_url = f"https://www.googleapis.com/drive/v3/files/{file_id}?alt=media"
        headers = {"Authorization": f"Bearer {creds.token}"}
        response = requests.get(download_url, headers=headers)
        response.raise_for_status()
        df = pd.read_csv(io.StringIO(response.text), encoding="latin-1", on_bad_lines="skip")
        dfs.append(df)
        
    df_all = pd.concat(dfs, ignore_index=True)
    df_all.columns = df_all.columns.str.strip()
    df_all['Data Atendimento'] = pd.to_datetime(df_all['Data Atendimento'], errors='coerce')
    df_all['Idade'] = pd.to_numeric(df_all['Idade'], errors='coerce')

    bins = [0,5,12,18,30,45,60,150]
    labels_ordered = ['0-5','6-12','13-18','19-30','31-45','46-60','60+']
    df_all['Faixa Etária'] = pd.cut(df_all['Idade'], bins=bins, labels=labels_ordered, ordered=True)
    return df_all

df = load_data()

min_date = df['Data Atendimento'].min().date()
max_date = df['Data Atendimento'].max().date()

st.sidebar.header("Filtros")

date_range = st.sidebar.date_input("Intervalo de Datas", value=(min_date,max_date), min_value=min_date, max_value=max_date)

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

top_n_proc = st.sidebar.selectbox("Top N Procedimentos", [10,20,30,'Todos'], index=0)
top_n_prof = st.sidebar.selectbox("Top N Profissionais", [10,20,30,'Todos'], index=0)

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

# Continue o código para calcular métricas, gerar gráficos e dashboards conforme sua necessidade

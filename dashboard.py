import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Observatório Gestor", layout="wide")

with st.sidebar:
    st.markdown("## Configuração")
    logo_cli = st.file_uploader("Logo do Cliente", type=["png", "jpg"])
    logo_emp = st.file_uploader("Logo da Sua Empresa", type=["png", "jpg"])
    uploaded_files = st.file_uploader("Selecionar arquivos CSV", type=["csv"], accept_multiple_files=True)
    graf_tamanho = st.selectbox("Tamanho dos Gráficos", options=["Pequeno", "Médio", "Grande"], index=1)

logo_cols = st.columns([1, 4, 1])
with logo_cols[0]:
    if logo_cli:
        st.image(logo_cli, width=120)
with logo_cols[1]:
    st.markdown(
        "<div style='text-align:center; margin-top:18px;'>"
        "<h1 style='font-size:2.3em; margin-bottom:0;'>Observatório Gestor</h1>"
        "</div>",
        unsafe_allow_html=True
    )
with logo_cols[2]:
    if logo_emp:
        st.image(logo_emp, width=120)

st.markdown("""
    <style>
    .card-container {
        display: flex;
        gap: 2em;
        margin-bottom: 2em;
        margin-top: 1.5em;
    }
    .card {
        flex: 1;
        background: #23242a;
        border-radius: 16px;
        padding: 1.2em 0.8em;
        text-align: center;
        box-shadow: 0 2px 8px rgba(44,50,64,0.12);
        min-width: 180px;
        max-width: 260px;
    }
    .verde  {color: #22d659; font-weight: bold; font-size: 2.1em;}
    .azul   {color: #309afc; font-weight: bold; font-size: 2.1em;}
    .rosa   {color: #f95faf; font-weight: bold; font-size: 2.1em;}
    .cinza  {color: #b9bbc7; font-weight: bold; font-size: 2.1em;}
    .card-label {margin-top: 0.3em; color: #b9bbc7; font-size: 1em;}
    </style>
""", unsafe_allow_html=True)

if uploaded_files:
    df_list = []
    for uploaded_file in uploaded_files:
        df_part = pd.read_csv(uploaded_file, on_bad_lines='skip', encoding='latin-1')
        df_list.append(df_part)
    df = pd.concat(df_list, ignore_index=True)

    if 'Data Atendimento' in df.columns:
        df['Data Atendimento'] = pd.to_datetime(df['Data Atendimento'], errors='coerce')
    if 'Idade' in df.columns:
        bins = [0,5,12,18,30,45,60,150]
        labels = ["0–5","6–12","13–18","19–30","31–45","46–60","60+"]
        df['Faixa Etária'] = pd.cut(df['Idade'], bins=bins, labels=labels, right=False)

    total = len(df)
    masc = len(df[df['Sexo'] == 'Masculino']) if 'Sexo' in df.columns else 0
    fem = len(df[df['Sexo'] == 'Feminino']) if 'Sexo' in df.columns else 0
    masc_pct = round(masc / total * 100, 1) if total > 0 else 0
    fem_pct = round(fem / total * 100, 1) if total > 0 else 0
    idade_media = round(df['Idade'].mean(), 1) if 'Idade' in df.columns else "N/A"

    st.markdown(f"""
    <div class="card-container">
        <div class="card"><span class="verde">{total}</span><div class="card-label">Total de Atendimentos</div></div>
        <div class="card"><span class="azul">{masc_pct}%</span><div class="card-label">Masculino</div></div>
        <div class="card"><span class="rosa">{fem_pct}%</span><div class="card-label">Feminino</div></div>
        <div class="card"><span class="cinza">{idade_media}</span><div class="card-label">Idade Média</div></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<h2 style='margin-top:0.2em;'>Análises e Gráficas</h2>", unsafe_allow_html=True)
    tam_map = {"Pequeno": 400, "Médio": 600, "Grande": 800}
    plot_height_small = tam_map[graf_tamanho]
    plot_height_large = 900

    expand_sexo = st.checkbox("Expandir Distribuição por Sexo", key="exp_sexo")
    if expand_sexo:
        sexo_counts = df['Sexo'].value_counts().reset_index() if 'Sexo' in df.columns else pd.DataFrame()
        if not sexo_counts.empty:
            sexo_counts.columns = ['Sexo', 'Quantidade']
            fig_sexo = px.pie(sexo_counts, names='Sexo', values='Quantidade', height=plot_height_large)
            st.plotly_chart(fig_sexo, use_container_width=True)
    else:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### Distribuição por Sexo")
            unique_sexos = sorted(df['Sexo'].dropna().unique()) if 'Sexo' in df.columns else []
            selected_sexo = st.selectbox("Selecione Sexo", ["Todos"] + unique_sexos, key="sexo_graf")
            df_sexo = df if selected_sexo == "Todos" else df[df['Sexo'] == selected_sexo]
            sexo_counts = df_sexo['Sexo'].value_counts().reset_index() if not df_sexo.empty and 'Sexo' in df_sexo.columns else pd.DataFrame()
            if not sexo_counts.empty:
                sexo_counts.columns = ['Sexo', 'Quantidade']
                fig_sexo = px.pie(sexo_counts, names='Sexo', values='Quantidade', height=plot_height_small)
                st.plotly_chart(fig_sexo, use_container_width=True, config={"displayModeBar": False})

        expand_faixa = st.checkbox("Expandir Distribuição por Faixa Etária", key="exp_faixa")
        if expand_faixa:
            unique_faixas = sorted(df['Faixa Etária'].dropna().unique()) if 'Faixa Etária' in df.columns else []
            df_faixa = df
            faixa_counts = df_faixa['Faixa Etária'].value_counts().sort_index().reset_index() if not df_faixa.empty and 'Faixa Etária' in df_faixa.columns else pd.DataFrame()
            if not faixa_counts.empty:
                faixa_counts.columns = ['Faixa Etária', 'Quantidade']
                fig_faixa = px.bar(faixa_counts, x='Faixa Etária', y='Quantidade', text='Quantidade', height=plot_height_large)
                st.plotly_chart(fig_faixa, use_container_width=True)
        else:
            with col2:
                st.markdown("#### Distribuição por Faixa Etária")
                unique_faixas = sorted(df['Faixa Etária'].dropna().unique()) if 'Faixa Etária' in df.columns else []
                selected_faixa = st.selectbox("Selecione Faixa Etária", ["Todas"] + unique_faixas, key="faixa_graf")
                df_faixa = df if selected_faixa == "Todas" else df[df['Faixa Etária'] == selected_faixa]
                faixa_counts = df_faixa['Faixa Etária'].value_counts().sort_index().reset_index() if not df_faixa.empty and 'Faixa Etária' in df_faixa.columns else pd.DataFrame()
                if not faixa_counts.empty:
                    faixa_counts.columns = ['Faixa Etária', 'Quantidade']
                    fig_faixa = px.bar(faixa_counts, x='Faixa Etária', y='Quantidade', text='Quantidade', height=plot_height_small)
                    st.plotly_chart(fig_faixa, use_container_width=True, config={"displayModeBar": False})

    expand_proc = st.checkbox("Expandir Top Procedimentos", key="exp_proc")
    if expand_proc:
        search_proc = st.text_input("Buscar Procedimento (deixe vazio para todos)", key="search_proc_exp")
        df_procs_filtered = df
        if search_proc:
            df_procs_filtered = df_procs_filtered[df_procs_filtered['Procedimento'].str.contains(search_proc, case=False, na=False)]
        top_proc_all = df_procs_filtered['Procedimento'].value_counts()
        top_proc = top_proc_all.reset_index()
        top_proc.columns = ['Procedimento', 'Quantidade']
        fig_proc = px.bar(top_proc, x='Procedimento', y='Quantidade', text='Quantidade', height=plot_height_large)
        st.plotly_chart(fig_proc, use_container_width=True)
    else:
        st.subheader("Top Procedimentos")
        search_proc = st.text_input("Buscar Procedimento (deixe vazio para todos)", key="search_proc")
        top_proc_options = [10, 20, 30, 40, 50, 'Todos']
        selected_top_proc = st.selectbox("Número de Top Procedimentos", top_proc_options, index=0)
        num_top_proc = None if selected_top_proc == 'Todos' else int(selected_top_proc)
        if 'Procedimento' in df.columns:
            df_procs_filtered = df
            if search_proc:
                df_procs_filtered = df_procs_filtered[df_procs_filtered['Procedimento'].str.contains(search_proc, case=False, na=False)]
            top_proc_all = df_procs_filtered['Procedimento'].value_counts()
            if num_top_proc:
                top_proc_all = top_proc_all.head(num_top_proc)
            top_proc = top_proc_all.reset_index()
            top_proc.columns = ['Procedimento', 'Quantidade']
            fig_proc = px.bar(top_proc, x='Procedimento', y='Quantidade', text='Quantidade', height=plot_height_small)
            st.plotly_chart(fig_proc, use_container_width=True, config={"displayModeBar": False})

    expand_prof = st.checkbox("Expandir Top Profissionais", key="exp_prof")
    if expand_prof:
        search_prof = st.text_input("Buscar Profissional (deixe vazio para todos)", key="search_prof_exp")
        df_profs_filtered = df
        if search_prof:
            df_profs_filtered = df_profs_filtered[df_profs_filtered['Profissional'].str.contains(search_prof, case=False, na=False)]
        top_prof_all = df_profs_filtered['Profissional'].value_counts()
        top_prof = top_prof_all.reset_index()
        top_prof.columns = ['Profissional', 'Quantidade']
        fig_prof = px.bar(top_prof, x='Profissional', y='Quantidade', text='Quantidade', height=plot_height_large)
        st.plotly_chart(fig_prof, use_container_width=True)
    else:
        st.subheader("Top Profissionais")
        search_prof = st.text_input("Buscar Profissional (deixe vazio para todos)", key="search_prof")
        top_prof_options = [10, 20, 30, 40, 50, 'Todos']
        selected_top_prof = st.selectbox("Número de Top Profissionais", top_prof_options, index=0)
        num_top_prof = None if selected_top_prof == 'Todos' else int(selected_top_prof)
        if 'Profissional' in df.columns:
            df_profs_filtered = df
            if search_prof:
                df_profs_filtered = df_profs_filtered[df_profs_filtered['Profissional'].str.contains(search_prof, case=False, na=False)]
            top_prof_all = df_profs_filtered['Profissional'].value_counts()
            if num_top_prof:
                top_prof_all = top_prof_all.head(num_top_prof)
            top_prof = top_prof_all.reset_index()
            top_prof.columns = ['Profissional', 'Quantidade']
            fig_prof = px.bar(top_prof, x='Profissional', y='Quantidade', text='Quantidade', height=plot_height_small)
            st.plotly_chart(fig_prof, use_container_width=True, config={"displayModeBar": False})

    expand_scatter = st.checkbox("Expandir Idade vs Procedimento", key="exp_scatter")
    if expand_scatter:
        if 'Idade' in df.columns and 'Procedimento' in df.columns:
            scatter_df = df.groupby(['Idade', 'Procedimento']).size().reset_index(name='Quantidade')
            fig_scatter = px.scatter(
                scatter_df, x='Idade', y='Procedimento', size='Quantidade',
                color='Quantidade', color_continuous_scale='Viridis',
                labels={"Quantidade": "Número de Atendimentos"}, height=plot_height_large
            )
            st.plotly_chart(fig_scatter, use_container_width=True)
    else:
        if 'Idade' in df.columns and 'Procedimento' in df.columns:
            st.subheader("Idade vs Procedimento")
            scatter_df = df.groupby(['Idade', 'Procedimento']).size().reset_index(name='Quantidade')
            fig_scatter = px.scatter(
                scatter_df, x='Idade', y='Procedimento', size='Quantidade',
                color='Quantidade', color_continuous_scale='Viridis',
                labels={"Quantidade": "Número de Atendimentos"}, height=plot_height_small
            )
            st.plotly_chart(fig_scatter, use_container_width=True, config={"displayModeBar": False})

    expand_linha = st.checkbox("Expandir Atendimentos por Dia", key="exp_linha")
    if expand_linha:
        if 'Data Atendimento' in df.columns:
            atendimentos_por_dia = df.groupby(df['Data Atendimento'].dt.date).size().reset_index(name='Quantidade')
            fig_linha = px.line(atendimentos_por_dia, x='Data Atendimento', y='Quantidade', markers=True, height=plot_height_large)
            st.plotly_chart(fig_linha, use_container_width=True)
    else:
        st.subheader("Atendimentos por Dia")
        if 'Data Atendimento' in df.columns:
            atendimentos_por_dia = df.groupby(df['Data Atendimento'].dt.date).size().reset_index(name='Quantidade')
            fig_linha = px.line(atendimentos_por_dia, x='Data Atendimento', y='Quantidade', markers=True, height=plot_height_small)
            st.plotly_chart(fig_linha, use_container_width=True, config={"displayModeBar": False})

    st.header("Resumo dos Dados Filtrados")
    if df.empty:
        st.write("Nenhum dado para mostrar com os filtros aplicados.")
    else:
        st.dataframe(df.head(5))
        st.markdown(f"*Mostrando as primeiras 5 linhas do total de {len(df)} registros filtrados.*")
else:
    st.info("Carregue pelo menos um arquivo CSV para iniciar.")

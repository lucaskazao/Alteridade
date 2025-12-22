"""
👥 Grupos Sociais - Análise Detalhada
Análise aprofundada da presença de ações afirmativas por grupo social
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.data_loader import load_all_areas, get_data_for_area, prepare_dataframe
from utils.filters import render_area_selector, render_global_filters
from config import GRUPOS_SOCIAIS, CORES

# Configuração da página
st.set_page_config(
    page_title="Grupos Sociais | Dashboard AA",
    page_icon="👥",
    layout="wide"
)

# Carregar dados
areas_data, df_todas_areas, lista_areas = load_all_areas()

# Sidebar
st.sidebar.markdown("# 👥 Grupos Sociais")
st.sidebar.markdown("Análise por grupo contemplado")
st.sidebar.markdown("---")

# Seletor de Área
area_selecionada = render_area_selector(lista_areas)

# Obter dados
df = get_data_for_area(area_selecionada, areas_data, df_todas_areas)
df = prepare_dataframe(df)

# Filtros
df_filtrado, filtros_ativos = render_global_filters(df)

# ==================== CONTEÚDO ====================

st.title("👥 Análise por Grupos Sociais")
st.markdown("Análise detalhada da presença de ações afirmativas por grupo social contemplado")
st.markdown("---")

# Preparar dados de grupos
grupos_stats = []

for nome_grupo, coluna in GRUPOS_SOCIAIS.items():
    if coluna in df_filtrado.columns:
        # Contar programas que contemplam o grupo
        programas_com_grupo = (df_filtrado[coluna].fillna('').str.strip().str.upper() == 'SIM').sum()
        
        # Tentar obter vagas do grupo
        coluna_vagas = f"Vagas {coluna.replace('AA ', '')}"
        if coluna_vagas in df_filtrado.columns:
            total_vagas = pd.to_numeric(df_filtrado[coluna_vagas], errors='coerce').fillna(0).sum()
        else:
            total_vagas = 0
        
        grupos_stats.append({
            'Grupo': nome_grupo,
            'Programas': int(programas_com_grupo),
            'Vagas': int(total_vagas),
            '% Programas': round((programas_com_grupo / len(df_filtrado) * 100), 1) if len(df_filtrado) > 0 else 0
        })

df_grupos = pd.DataFrame(grupos_stats).sort_values('Programas', ascending=False)

# Visão Geral
st.markdown("## 📊 Visão Geral dos Grupos")

col1, col2 = st.columns([2, 1])

with col1:
    # Gráfico de barras - Programas por grupo
    fig_bar = px.bar(
        df_grupos,
        x='Grupo',
        y='Programas',
        title='Número de Programas que Contemplam Cada Grupo',
        text='Programas',
        color='Programas',
        color_continuous_scale='Viridis'
    )
    fig_bar.update_traces(textposition='outside')
    fig_bar.update_layout(
        xaxis_title='Grupo Social',
        yaxis_title='Quantidade de Programas',
        showlegend=False,
        height=400
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with col2:
    # Tabela resumo
    st.markdown("**Resumo por Grupo:**")
    st.dataframe(
        df_grupos[['Grupo', 'Programas', 'Vagas', '% Programas']],
        use_container_width=True,
        hide_index=True,
        height=400
    )

st.markdown("---")

# Gráficos de Distribuição (Programas e Vagas)
st.markdown("## 📈 Distribuição de Programas e Vagas")

col_pie1, col_pie2 = st.columns(2)

with col_pie1:
    # Pizza: Distribuição de Programas
    df_top5 = df_grupos.head(5)
    outros_programas = df_grupos.iloc[5:]['Programas'].sum() if len(df_grupos) > 5 else 0
    
    if outros_programas > 0:
        df_top5_plot = pd.concat([
            df_top5,
            pd.DataFrame([{'Grupo': 'Outros', 'Programas': outros_programas}])
        ])
    else:
        df_top5_plot = df_top5
    
    fig_pie = px.pie(
        df_top5_plot,
        values='Programas',
        names='Grupo',
        title='Distribuição de Programas por Grupo',
        hole=0.4
    )
    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig_pie, use_container_width=True)

with col_pie2:
    # Treemap: Distribuição de Vagas
    # Filtrar apenas grupos com vagas > 0
    df_vagas = df_grupos[df_grupos['Vagas'] > 0]
    
    if not df_vagas.empty:
        fig_tree = px.treemap(
            df_vagas,
            path=['Grupo'],
            values='Vagas',
            title='Distribuição de Vagas por Grupo (Treemap)',
            color='Vagas',
            color_continuous_scale='Greens'
        )
        st.plotly_chart(fig_tree, use_container_width=True)
    else:
        st.info("Dados de vagas não disponíveis para gerar o gráfico.")

# Métricas Gerais
st.markdown("### Métricas Gerais")
col_m1, col_m2, col_m3 = st.columns(3)

with col_m1:
    if len(df_grupos) > 0:
        grupo_mais_contemplado = df_grupos.iloc[0]
        st.metric(
            "Grupo Mais Contemplado",
            grupo_mais_contemplado['Grupo'],
            f"{grupo_mais_contemplado['Programas']} programas"
        )

with col_m2:
    total_programas_com_grupos = df_grupos['Programas'].sum()
    st.metric(
        "Total de Contemplações",
        f"{total_programas_com_grupos:,}",
        help="Soma de todos os programas que contemplam cada grupo"
    )

with col_m3:
    media_grupos_por_programa = total_programas_com_grupos / len(df_filtrado) if len(df_filtrado) > 0 else 0
    st.metric(
        "Média de Grupos/Programa",
        f"{media_grupos_por_programa:.1f}",
        help="Média de grupos contemplados por programa"
    )

st.markdown("---")

# Radar Chart: Perfil Regional
st.markdown("## 🕸️ Perfil Regional de Inclusão")
st.markdown("Comparação da cobertura de grupos sociais por região.")

if 'Região' in df_filtrado.columns:
    # Preparar dados para Radar
    # Eixos: Grupos, Linhas: Regiões, Valores: % de programas da região que atendem o grupo
    
    radar_data = []
    regioes = sorted(df_filtrado['Região'].dropna().unique())
    grupos_radar = df_grupos['Grupo'].tolist()  # Todos os grupos
    
    fig_radar = go.Figure()
    
    for regiao in regioes:
        df_reg = df_filtrado[df_filtrado['Região'] == regiao]
        total_reg = len(df_reg)
        
        if total_reg > 0:
            valores = []
            for grupo in grupos_radar:
                col = GRUPOS_SOCIAIS[grupo]
                if col in df_reg.columns:
                    qtd = (df_reg[col].fillna('').str.strip().str.upper() == 'SIM').sum()
                    valores.append((qtd / total_reg) * 100)
                else:
                    valores.append(0)
            
            # Fechar o ciclo do radar
            valores_plot = valores + [valores[0]]
            grupos_plot = grupos_radar + [grupos_radar[0]]
            
            fig_radar.add_trace(go.Scatterpolar(
                r=valores_plot,
                theta=grupos_plot,
                fill='toself',
                name=regiao
            ))
            
    fig_radar.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )
        ),
        showlegend=True,
        height=500,
        title="Percentual de Programas por Região que Contemplam cada Grupo"
    )
    
    st.plotly_chart(fig_radar, use_container_width=True)
else:
    st.info("Dados regionais não disponíveis para o gráfico de radar.")

st.markdown("---")

# Análise Detalhada por Grupo Selecionado
st.markdown("## 🔍 Análise Detalhada por Grupo")

grupo_selecionado = st.selectbox(
    "Selecione um grupo para análise detalhada:",
    options=df_grupos['Grupo'].tolist()
)

if grupo_selecionado:
    coluna_grupo = GRUPOS_SOCIAIS[grupo_selecionado]
    
    # Filtrar programas que contemplam o grupo
    df_grupo = df_filtrado[df_filtrado[coluna_grupo].fillna('').str.strip().str.upper() == 'SIM'].copy()
    
    st.markdown(f"### Análise: {grupo_selecionado}")
    
    col_metric1, col_metric2, col_metric3 = st.columns(3)
    
    with col_metric1:
        st.metric("Programas", len(df_grupo))
    
    with col_metric2:
        perc = (len(df_grupo) / len(df_filtrado) * 100) if len(df_filtrado) > 0 else 0
        st.metric("% do Total", f"{perc:.1f}%")
    
    with col_metric3:
        # Vagas (se disponível)
        coluna_vagas = f"Vagas {coluna_grupo.replace('AA ', '')}"
        if coluna_vagas in df_grupo.columns:
            total_vagas_grupo = pd.to_numeric(df_grupo[coluna_vagas], errors='coerce').fillna(0).sum()
            st.metric("Total de Vagas", f"{int(total_vagas_grupo):,}")
    
    st.markdown("---")
    
    # Distribuição por Região
    col_regiao, col_nota = st.columns(2)
    
    with col_regiao:
        if 'Região' in df_grupo.columns and len(df_grupo) > 0:
            regiao_counts = df_grupo['Região'].value_counts()
            
            fig_regiao = px.bar(
                x=regiao_counts.index,
                y=regiao_counts.values,
                title=f'Distribuição Geográfica - {grupo_selecionado}',
                labels={'x': 'Região', 'y': 'Quantidade de Programas'},
                text=regiao_counts.values
            )
            fig_regiao.update_traces(textposition='outside', marker_color=CORES['primaria'])
            fig_regiao.update_layout(showlegend=False, height=350)
            st.plotly_chart(fig_regiao, use_container_width=True)
    
    with col_nota:
        if 'NOTA' in df_grupo.columns and len(df_grupo) > 0:
            nota_counts = df_grupo['NOTA'].value_counts()
            
            fig_nota = px.bar(
                x=nota_counts.index,
                y=nota_counts.values,
                title=f'Distribuição por Nota CAPES - {grupo_selecionado}',
                labels={'x': 'Nota', 'y': 'Quantidade de Programas'},
                text=nota_counts.values,
                category_orders={'x': ['A', '3', '4', '5', '6', '7']}
            )
            fig_nota.update_traces(textposition='outside', marker_color=CORES['secundaria'])
            fig_nota.update_layout(showlegend=False, height=350)
            st.plotly_chart(fig_nota, use_container_width=True)
    
    st.markdown("---")
    
    # Tabela de programas
    st.markdown(f"### Programas que Contemplam {grupo_selecionado}")
    
    if len(df_grupo) > 0:
        colunas_exibir = ['Nome do Programa', 'Sigla da IES', 'UF', 'Região', 'NOTA', 'Tipo de IES', 'Modalidade de Ensino']
        colunas_disponiveis = [col for col in colunas_exibir if col in df_grupo.columns]
        
        st.dataframe(
            df_grupo[colunas_disponiveis].reset_index(drop=True),
            use_container_width=True,
            height=400
        )
        
        # Opção de download
        csv = df_grupo[colunas_disponiveis].to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label=f"📥 Download Lista - {grupo_selecionado}",
            data=csv,
            file_name=f"programas_{grupo_selecionado.replace(' ', '_').lower()}.csv",
            mime="text/csv",
        )
    else:
        st.info(f"Nenhum programa encontrado para {grupo_selecionado} com os filtros atuais.")

st.markdown("---")

# Análise de Múltiplos Grupos
st.markdown("## 🔗 Programas com Múltiplos Grupos")

# Calcular quantos grupos cada programa contempla
grupos_por_programa = []

for idx, row in df_filtrado.iterrows():
    grupos_contemplados = []
    for nome_grupo, coluna in GRUPOS_SOCIAIS.items():
        if coluna in df_filtrado.columns:
            if str(row[coluna]).strip().upper() == 'SIM':
                grupos_contemplados.append(nome_grupo)
    
    if len(grupos_contemplados) > 0:
        grupos_por_programa.append({
            'Programa': row.get('Nome do Programa', 'N/A'),
            'Quantidade': len(grupos_contemplados),
            'Grupos': ', '.join(grupos_contemplados)
        })

if grupos_por_programa:
    df_multiplos = pd.DataFrame(grupos_por_programa).sort_values('Quantidade', ascending=False)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Distribuição de quantidade de grupos
        quant_groups = df_multiplos['Quantidade'].value_counts().sort_index()
        
        fig_multi = px.bar(
            x=quant_groups.index,
            y=quant_groups.values,
            title='Distribuição de Programas por Nº de Grupos',
            labels={'x': 'Quantidade de Grupos', 'y': 'Quantidade de Programas'},
            text=quant_groups.values
        )
        fig_multi.update_traces(textposition='outside', marker_color=CORES['terciaria'])
        fig_multi.update_layout(showlegend=False)
        st.plotly_chart(fig_multi, use_container_width=True)
    
    with col2:
        # Top programas com mais grupos
        st.markdown("**Top 10 Programas - Mais Grupos Contemplados:**")
        st.dataframe(
            df_multiplos.head(10),
            use_container_width=True,
            hide_index=True,
            height=400
        )
else:
    st.info("Nenhum programa contempla grupos sociais com os filtros atuais.")

st.markdown("---")

# Análise de Múltiplos Grupos por Área
st.markdown("## 🧩 Interseccionalidade por Área")
st.markdown("Análise da média de grupos sociais contemplados por programa em cada área.")

if 'Área' in df_filtrado.columns:
    # Calcular grupos por programa (reaproveitando lógica ou recalculando para garantir)
    data_area = []
    
    # Iterar sobre o dataframe filtrado
    for idx, row in df_filtrado.iterrows():
        count_grupos = 0
        for _, col in GRUPOS_SOCIAIS.items():
            if col in df_filtrado.columns:
                if str(row[col]).strip().upper() == 'SIM':
                    count_grupos += 1
        
        data_area.append({
            'Área': row['Área'],
            'Qtd Grupos': count_grupos
        })
    
    if data_area:
        df_area_groups = pd.DataFrame(data_area)
        
        # Agrupar por área e calcular média
        area_stats = df_area_groups.groupby('Área')['Qtd Grupos'].mean().reset_index()
        area_stats = area_stats.sort_values('Qtd Grupos', ascending=False)
        area_stats.columns = ['Área', 'Média de Grupos por Programa']
        
        # Gráfico
        fig_area = px.bar(
            area_stats,
            x='Área',
            y='Média de Grupos por Programa',
            title='Média de Grupos Sociais Contemplados por Programa (por Área)',
            text='Média de Grupos por Programa',
            color='Média de Grupos por Programa',
            color_continuous_scale='Blues'
        )
        fig_area.update_traces(texttemplate='%{text:.2f}', textposition='outside')
        fig_area.update_layout(height=500)
        
        st.plotly_chart(fig_area, use_container_width=True)
        
        # Mostrar tabela se houver mais de uma área
        if len(area_stats) > 1:
            with st.expander("Ver dados detalhados por área"):
                st.dataframe(area_stats, use_container_width=True)
    else:
        st.info("Não há dados suficientes para análise por área.")
else:
    st.info("A coluna 'Área' não está disponível nos dados atuais. Selecione 'Todas as Áreas' para ver esta análise.")

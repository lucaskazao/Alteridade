"""
📊 Análise de Vagas - Distribuição e Comparações
Análise detalhada da distribuição de vagas AA por diferentes dimensões
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.data_loader import load_all_areas, get_data_for_area, prepare_dataframe
from utils.filters import render_area_selector, render_global_filters
from config import CORES, COLUNAS_VAGAS

# Configuração da página
st.set_page_config(
    page_title="Análise de Vagas | Dashboard AA",
    page_icon="📊",
    layout="wide"
)

# Carregar dados
areas_data, df_todas_areas, lista_areas = load_all_areas()

# Sidebar
st.sidebar.markdown("# 📊 Análise de Vagas")
st.sidebar.markdown("Distribuição e estatísticas de vagas")
st.sidebar.markdown("---")

# Seletor de Área
area_selecionada = render_area_selector(lista_areas)

# Obter dados
df = get_data_for_area(area_selecionada, areas_data, df_todas_areas)
df = prepare_dataframe(df)

# Filtros
df_filtrado, filtros_ativos = render_global_filters(df)

# ==================== PROCESSAMENTO DE DADOS ====================

# Converter colunas de vagas para numérico

# Corrigir nome da coluna para compatibilidade
colunas_vagas_corrigidas = ['Qnt Vagas Totais', 'Vagas Totais AA', 'Vagas Totais Agregadas', 'Vagas Totais Por Grupo/Exclusivas']
for col in colunas_vagas_corrigidas:
    if col in df_filtrado.columns:
        df_filtrado[col] = pd.to_numeric(df_filtrado[col], errors='coerce').fillna(0)

# Calcular totais
total_vagas_gerais = df_filtrado['Qnt Vagas Totais'].sum()
total_vagas_aa = df_filtrado['Vagas Totais AA'].sum()
total_vagas_agregadas = df_filtrado['Vagas Totais Agregadas'].sum()
total_vagas_por_grupo = df_filtrado['Vagas Totais Por Grupo/Exclusivas'].sum()

# ==================== CONTEÚDO ====================

st.title("📊 Análise de Distribuição de Vagas")
st.markdown("Análise detalhada de vagas totais e vagas destinadas a ações afirmativas")
st.markdown("---")

# Métricas Principais
st.markdown("## 📈 Visão Geral das Vagas")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Vagas Totais",
        f"{int(total_vagas_gerais):,}",
        help="Total de vagas em todos os programas"
    )

with col2:
    perc_aa = (total_vagas_aa / total_vagas_gerais * 100) if total_vagas_gerais > 0 else 0
    st.metric(
        "Vagas AA",
        f"{int(total_vagas_aa):,}",
        delta=f"{perc_aa:.1f}%",
        help="Vagas destinadas a ações afirmativas"
    )

with col3:
    st.metric(
        "Vagas Agregadas",
        f"{int(total_vagas_agregadas):,}",
        help="Vagas AA sem especificação por grupo"
    )

with col4:
    st.metric(
        "Vagas Por Grupo",
        f"{int(total_vagas_por_grupo):,}",
        help="Vagas AA com especificação por grupo"
    )

st.markdown("---")

# Visualizações Comparativas
st.markdown("## 📊 Comparação de Categorias de Vagas")

col_grafico, col_prop = st.columns([2, 1])

with col_grafico:
    # Gráfico de barras comparativo
    categorias = ['Vagas Totais', 'Vagas AA\n(Total)', 'Vagas\nAgregadas', 'Vagas Por\nGrupo']
    valores = [total_vagas_gerais, total_vagas_aa, total_vagas_agregadas, total_vagas_por_grupo]
    cores = [CORES['primaria'], CORES['com_aa'], CORES['secundaria'], CORES['terciaria']]
    
    fig_vagas = go.Figure()
    fig_vagas.add_trace(go.Bar(
        x=categorias,
        y=valores,
        marker_color=cores,
        text=valores,
        textposition='outside',
        texttemplate='%{text:,.0f}'
    ))
    
    fig_vagas.update_layout(
        title='Distribuição Total de Vagas por Categoria',
        xaxis_title='Categoria de Vagas',
        yaxis_title='Quantidade de Vagas',
        showlegend=False,
        height=400
    )
    st.plotly_chart(fig_vagas, use_container_width=True)

with col_prop:
    # Gráfico de proporção
    st.markdown("**Proporção de Vagas AA:**")
    
    if total_vagas_gerais > 0:
        fig_prop = px.pie(
            values=[total_vagas_aa, total_vagas_gerais - total_vagas_aa],
            names=['Vagas AA', 'Ampla Concorrência'],
            color_discrete_sequence=[CORES['com_aa'], CORES['neutra']],
            hole=0.4
        )
        fig_prop.update_traces(textposition='inside', textinfo='percent+label')
        fig_prop.update_layout(height=350, showlegend=True)
        st.plotly_chart(fig_prop, use_container_width=True)
    
    # Estatísticas
    st.markdown("**Estatísticas:**")
    programas_com_aa = (df_filtrado['Vagas Totais AA'] > 0).sum()
    programas_com_agregadas = (df_filtrado['Vagas Totais Agregadas'] > 0).sum()
    programas_com_grupo = (df_filtrado['Vagas Totais Por Grupo/Exclusivas'] > 0).sum()
    
    st.metric("Programas com Vagas AA", programas_com_aa)
    st.metric("Com Agregadas", programas_com_agregadas)
    st.metric("Com Por Grupo", programas_com_grupo)

st.markdown("---")

# Distribuição por Região
st.markdown("## 🗺️ Distribuição de Vagas por Região")

if 'Região' in df_filtrado.columns:
    # Agregar vagas por região
    vagas_por_regiao = df_filtrado.groupby('Região').agg({
        'Qnt Vagas Totais': 'sum',
        'Vagas Totais AA': 'sum',
        'Vagas Totais Agregadas': 'sum',
        'Vagas Totais Por Grupo/Exclusivas': 'sum'
    }).reset_index()
    
    col_reg1, col_reg2 = st.columns(2)
    
    with col_reg1:
        # Gráfico de barras empilhadas
        fig_regiao = go.Figure()
        
        fig_regiao.add_trace(go.Bar(
            name='Vagas AA',
            x=vagas_por_regiao['Região'],
            y=vagas_por_regiao['Vagas Totais AA'],
            marker_color=CORES['com_aa']
        ))
        
        fig_regiao.add_trace(go.Bar(
            name='Ampla Concorrência',
            x=vagas_por_regiao['Região'],
            y=vagas_por_regiao['Qnt Vagas Totais'] - vagas_por_regiao['Vagas Totais AA'],
            marker_color=CORES['neutra']
        ))
        
        fig_regiao.update_layout(
            title='Vagas por Região (AA vs Ampla Concorrência)',
            xaxis_title='Região',
            yaxis_title='Quantidade de Vagas',
            barmode='stack',
            height=400
        )
        st.plotly_chart(fig_regiao, use_container_width=True)
    
    with col_reg2:
        # Tabela resumo
        st.markdown("**Tabela Resumo - Vagas por Região:**")
        vagas_por_regiao['% AA'] = (
            vagas_por_regiao['Vagas Totais AA'] / vagas_por_regiao['Qnt Vagas Totais'] * 100
        ).round(1)
        
        st.dataframe(
            vagas_por_regiao[['Região', 'Qnt Vagas Totais', 'Vagas Totais AA', '% AA']],
            use_container_width=True,
            hide_index=True
        )

st.markdown("---")

# Distribuição por Nota CAPES
st.markdown("## ⭐ Distribuição de Vagas por Nota CAPES")

if 'NOTA' in df_filtrado.columns:
    from config import ORDEM_NOTAS
    
    # Agregar vagas por nota
    vagas_por_nota = df_filtrado.groupby('NOTA').agg({
        'Qnt Vagas Totais': 'sum',
        'Vagas Totais AA': 'sum'
    }).reset_index()
    
    # Ordenar por nota
    vagas_por_nota['NOTA'] = pd.Categorical(vagas_por_nota['NOTA'], categories=ORDEM_NOTAS, ordered=True)
    vagas_por_nota = vagas_por_nota.sort_values('NOTA')
    
    col_nota1, col_nota2 = st.columns(2)
    
    with col_nota1:
        # Gráfico de linhas
        fig_nota = go.Figure()
        
        fig_nota.add_trace(go.Scatter(
            x=vagas_por_nota['NOTA'],
            y=vagas_por_nota['Qnt Vagas Totais'],
            mode='lines+markers',
            name='Vagas Totais',
            line=dict(color=CORES['primaria'], width=3),
            marker=dict(size=10)
        ))
        
        fig_nota.add_trace(go.Scatter(
            x=vagas_por_nota['NOTA'],
            y=vagas_por_nota['Vagas Totais AA'],
            mode='lines+markers',
            name='Vagas AA',
            line=dict(color=CORES['com_aa'], width=3),
            marker=dict(size=10)
        ))
        
        fig_nota.update_layout(
            title='Vagas por Nota CAPES',
            xaxis_title='Nota',
            yaxis_title='Quantidade de Vagas',
            height=400
        )
        st.plotly_chart(fig_nota, use_container_width=True)
    
    with col_nota2:
        # Percentual de vagas AA por nota
        vagas_por_nota['% AA'] = (
            vagas_por_nota['Vagas Totais AA'] / vagas_por_nota['Qnt Vagas Totais'] * 100
        ).round(1)
        
        fig_perc = px.bar(
            vagas_por_nota,
            x='NOTA',
            y='% AA',
            title='Percentual de Vagas AA por Nota',
            text='% AA',
            color='% AA',
            color_continuous_scale='Viridis'
        )
        fig_perc.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig_perc.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig_perc, use_container_width=True)

st.markdown("---")

# Análise de Médias
st.markdown("## 📈 Análise de Médias de Vagas")

col_media1, col_media2, col_media3 = st.columns(3)

# Programas com AA vs sem AA
df_com_aa = df_filtrado[df_filtrado['Status AA'] == 'Com Editais AA']
df_sem_aa = df_filtrado[df_filtrado['Status AA'] == 'Sem Editais AA']

with col_media1:
    st.markdown("### Por Status de AA")
    
    media_com_aa = df_com_aa['Qnt Vagas Totais'].mean() if len(df_com_aa) > 0 else 0
    media_sem_aa = df_sem_aa['Qnt Vagas Totais'].mean() if len(df_sem_aa) > 0 else 0
    
    fig_media_status = go.Figure()
    fig_media_status.add_trace(go.Bar(
        x=['Com AA', 'Sem AA'],
        y=[media_com_aa, media_sem_aa],
        marker_color=[CORES['com_aa'], CORES['sem_aa']],
        text=[f'{media_com_aa:.1f}', f'{media_sem_aa:.1f}'],
        textposition='auto'
    ))
    fig_media_status.update_layout(
        title='Média de Vagas Totais',
        yaxis_title='Média de Vagas',
        showlegend=False,
        height=300
    )
    st.plotly_chart(fig_media_status, use_container_width=True)

with col_media2:
    st.markdown("### Por Região")
    
    if 'Região' in df_filtrado.columns:
        media_por_regiao = df_filtrado.groupby('Região')['Qnt Vagas Totais'].mean().sort_values(ascending=False)
        
        fig_media_regiao = px.bar(
            x=media_por_regiao.index,
            y=media_por_regiao.values,
            title='Média de Vagas por Região',
            labels={'x': 'Região', 'y': 'Média de Vagas'},
            text=media_por_regiao.values
        )
        fig_media_regiao.update_traces(texttemplate='%{text:.1f}', textposition='outside', marker_color=CORES['primaria'])
        fig_media_regiao.update_layout(showlegend=False, height=300)
        st.plotly_chart(fig_media_regiao, use_container_width=True)

with col_media3:
    st.markdown("### Por Tipo de IES")
    
    if 'Tipo de IES' in df_filtrado.columns:
        media_por_ies = df_filtrado.groupby('Tipo de IES')['Qnt Vagas Totais'].mean().sort_values(ascending=False)
        
        fig_media_ies = px.bar(
            x=media_por_ies.index,
            y=media_por_ies.values,
            title='Média de Vagas por Tipo IES',
            labels={'x': 'Tipo de IES', 'y': 'Média de Vagas'},
            text=media_por_ies.values
        )
        fig_media_ies.update_traces(texttemplate='%{text:.1f}', textposition='outside', marker_color=CORES['secundaria'])
        fig_media_ies.update_layout(showlegend=False, height=300)
        st.plotly_chart(fig_media_ies, use_container_width=True)

st.markdown("---")

# Top Programas
st.markdown("## 🏆 Top Programas com Mais Vagas AA")

df_top_aa = df_filtrado[df_filtrado['Vagas Totais AA'] > 0].nlargest(10, 'Vagas Totais AA')

if len(df_top_aa) > 0:
    col_top1, col_top2 = st.columns([1, 1])
    
    with col_top1:
        fig_top = px.bar(
            df_top_aa,
            y='Nome do Programa',
            x='Vagas Totais AA',
            orientation='h',
            title='Top 10 Programas - Mais Vagas AA',
            text='Vagas Totais AA',
            color='Vagas Totais AA',
            color_continuous_scale='Viridis'
        )
        fig_top.update_traces(textposition='outside')
        fig_top.update_layout(yaxis={'categoryorder':'total ascending'}, height=500, showlegend=False)
        st.plotly_chart(fig_top, use_container_width=True)
    
    with col_top2:
        st.markdown("**Detalhes dos Top 10:**")
        colunas_exibir = ['Nome do Programa', 'Sigla da IES', 'UF', 'NOTA', 'Vagas Totais AA']
        st.dataframe(
            df_top_aa[colunas_exibir].reset_index(drop=True),
            use_container_width=True,
            height=500
        )
else:
    st.info("Nenhum programa com vagas AA encontrado com os filtros atuais.")

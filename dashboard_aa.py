"""
🏠 Dashboard de Ações Afirmativas - CAPES
Página Principal / Home
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.data_loader import load_all_areas, get_data_for_area, get_summary_stats, prepare_dataframe
from utils.filters import render_area_selector, render_global_filters

# Configuração da página
st.set_page_config(
    page_title="Dashboard Ações Afirmativas - CAPES",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Carregar dados (com cache)
areas_data, df_todas_areas, lista_areas = load_all_areas()

# ==================== SIDEBAR ====================
st.sidebar.image("https://via.placeholder.com/300x80/2C3E50/FFFFFF?text=CAPES", use_container_width=True)
st.sidebar.markdown("# 📊 Dashboard AA")
st.sidebar.markdown("**Colégio de Humanidades**")
st.sidebar.markdown("---")

# Seletor de Área
area_selecionada = render_area_selector(lista_areas)

# Obter dados da área selecionada
df = get_data_for_area(area_selecionada, areas_data, df_todas_areas)
df = prepare_dataframe(df)

# Aplicar filtros globais
df_filtrado, filtros_ativos = render_global_filters(df)

# ==================== CONTEÚDO PRINCIPAL ====================

# Cabeçalho
st.title("📊 Dashboard de Ações Afirmativas - CAPES")
st.markdown("### Análise de Políticas de Ações Afirmativas em Programas de Pós-Graduação")
st.markdown("---")

# Calcular estatísticas
stats = get_summary_stats(df_filtrado)

# Métricas Principais em Destaque
st.markdown("## 📈 Visão Geral")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total de Programas", 
        stats['total_programas'],
        help="Total de programas de pós-graduação analisados"
    )
    
with col2:
    st.metric(
        "Com Editais AA", 
        stats['com_aa'],
        delta=f"{stats['percentual_aa']:.1f}%",
        delta_color="normal",
        help="Programas que possuem editais de ações afirmativas"
    )
    
with col3:
    st.metric(
        "Sem Editais AA", 
        stats['sem_aa'],
        delta=f"{100-stats['percentual_aa']:.1f}%",
        delta_color="inverse",
        help="Programas sem editais de ações afirmativas"
    )
    
with col4:
    st.metric(
        "Total de Vagas AA", 
        f"{stats['total_vagas_aa']:,}",
        help="Total de vagas destinadas a ações afirmativas"
    )

st.markdown("---")

# Gráficos de Resumo
st.markdown("## 📊 Distribuição de Ações Afirmativas")

col_left, col_right = st.columns(2)

with col_left:
    # Gráfico de pizza
    fig_pie = px.pie(
        values=[stats['com_aa'], stats['sem_aa']],
        names=['Com Editais AA', 'Sem Editais AA'],
        title='Presença de Editais de Ações Afirmativas',
        color_discrete_sequence=['#2ecc71', '#e74c3c'],
        hole=0.4
    )
    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
    fig_pie.update_layout(height=400)
    st.plotly_chart(fig_pie, use_container_width=True)

with col_right:
    # Gráfico de barras
    status_counts = df_filtrado['Status AA'].value_counts()
    fig_bar = go.Figure(data=[
        go.Bar(
            x=status_counts.index,
            y=status_counts.values,
            marker_color=['#2ecc71' if 'Com' in idx else '#e74c3c' for idx in status_counts.index],
            text=status_counts.values,
            textposition='auto'
        )
    ])
    fig_bar.update_layout(
        title='Quantidade de Programas por Status',
        xaxis_title='Status',
        yaxis_title='Quantidade',
        showlegend=False,
        height=400
    )
    st.plotly_chart(fig_bar, use_container_width=True)

st.markdown("---")

# Cards de Navegação
st.markdown("## 🧭 Navegação Rápida")
st.markdown("Explore análises detalhadas nas páginas abaixo:")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    ### 📈 Visão Geral
    Análises detalhadas por:
    - Nota CAPES
    - Região
    - Modalidade de Ensino
    - Tipo de IES
    - Tipo de AA
    """)
    
with col2:
    st.markdown("""
    ### 👥 Grupos Sociais
    Análise aprofundada de:
    - Pretos e Pardos
    - PcD
    - Indígenas
    - Quilombolas
    - E outros grupos
    """)
    
with col3:
    st.markdown("""
    ### 📥 Exportar Dados
    Gere relatórios em:
    - Excel
    - CSV
    - PDF (em breve)
    """)

st.markdown("---")

# Insights Rápidos
st.markdown("## 💡 Insights Rápidos")

# Preparar dados para insights
if len(df_filtrado) > 0:
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Região com mais AA
        if 'Região' in df_filtrado.columns:
            regiao_top = df_filtrado[df_filtrado['Status AA'] == 'Com Editais AA']['Região'].value_counts()
            if len(regiao_top) > 0:
                st.info(f"""
                **🗺️ Região Destaque**  
                A região **{regiao_top.index[0]}** possui o maior número de programas com AA: **{regiao_top.values[0]}** programas
                """)
    
    with col2:
        # Nota mais comum com AA
        if 'NOTA' in df_filtrado.columns:
            nota_top = df_filtrado[df_filtrado['Status AA'] == 'Com Editais AA']['NOTA'].value_counts()
            if len(nota_top) > 0:
                st.success(f"""
                **⭐ Nota Destaque**  
                Programas com nota **{nota_top.index[0]}** têm maior presença de AA: **{nota_top.values[0]}** programas
                """)
    
    with col3:
        # Percentual de vagas AA
        if stats['total_vagas'] > 0:
            perc_vagas_aa = (stats['total_vagas_aa'] / stats['total_vagas'] * 100)
            st.warning(f"""
            **📊 Vagas AA**  
            **{perc_vagas_aa:.1f}%** do total de vagas são destinadas a ações afirmativas
            """)

# Rodapé
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #7f8c8d;'>
    <p>Dashboard de Ações Afirmativas - CAPES | Colégio de Humanidades</p>
    <p style='font-size: 0.8em;'>Dados atualizados em 2025 | Desenvolvido para análise de políticas de inclusão</p>
</div>
""", unsafe_allow_html=True)

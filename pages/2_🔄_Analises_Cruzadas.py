"""
🔄 Análises Cruzadas - Correlações e Comparações
Análise de correlações e cruzamentos entre diferentes variáveis
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from utils.data_loader import load_all_areas, get_data_for_area, prepare_dataframe
from utils.filters import render_area_selector, render_global_filters
from config import CORES, ORDEM_NOTAS

# Configuração da página
st.set_page_config(
    page_title="Análises Cruzadas | Dashboard AA",
    page_icon="🔄",
    layout="wide"
)

# Carregar dados
areas_data, df_todas_areas, lista_areas = load_all_areas()

# Sidebar
st.sidebar.markdown("# 🔄 Análises Cruzadas")
st.sidebar.markdown("Correlações e cruzamentos")
st.sidebar.markdown("---")

# Seletor de Área
area_selecionada = render_area_selector(lista_areas)

# Obter dados
df = get_data_for_area(area_selecionada, areas_data, df_todas_areas)
df = prepare_dataframe(df)

# Filtros
df_filtrado, filtros_ativos = render_global_filters(df)

# ==================== PREPARAÇÃO DOS DADOS ====================

# Converter colunas numéricas
colunas_numericas = ['Qnt. Vagas Totais', 'Vagas Totais AA', 'Vagas Totais Agregadas', 'Vagas Totais Por Grupo/Exclusivas']
for col in colunas_numericas:
    if col in df_filtrado.columns:
        df_filtrado[col] = pd.to_numeric(df_filtrado[col], errors='coerce').fillna(0)

# Criar variável binária para AA
df_filtrado['Tem_AA'] = (df_filtrado['Status AA'] == 'Com Editais AA').astype(int)

# ==================== CONTEÚDO ====================

st.title("🔄 Análises Cruzadas")
st.markdown("Explore correlações e relações entre diferentes dimensões dos dados")
st.markdown("---")

# Análise: Nota x Região
st.markdown("## 🗺️ Cruzamento: Nota CAPES x Região")

if 'NOTA' in df_filtrado.columns and 'Região' in df_filtrado.columns:
    # Criar tabela cruzada
    crosstab_nota_regiao = pd.crosstab(
        df_filtrado['Região'],
        df_filtrado['NOTA']
    )
    
    # Ordenar colunas por ordem de notas
    colunas_ordenadas = [n for n in ORDEM_NOTAS if n in crosstab_nota_regiao.columns]
    crosstab_nota_regiao = crosstab_nota_regiao[colunas_ordenadas]
    
    col_heat1, col_table1 = st.columns([2, 1])
    
    with col_heat1:
        # Heatmap
        fig_heat_nota_regiao = go.Figure(data=go.Heatmap(
            z=crosstab_nota_regiao.values,
            x=crosstab_nota_regiao.columns,
            y=crosstab_nota_regiao.index,
            texttemplate='%{z}',
            textfont={"size": 12},
            colorscale='Viridis',
            colorbar=dict(title="Programas")
        ))
        
        fig_heat_nota_regiao.update_layout(
            title='Distribuição de Programas: Nota x Região',
            xaxis_title='Nota CAPES',
            yaxis_title='Região',
            height=400
        )
        st.plotly_chart(fig_heat_nota_regiao, use_container_width=True)
    
    with col_table1:
        st.markdown("**Tabela de Frequência:**")
        st.dataframe(crosstab_nota_regiao, use_container_width=True, height=400)
    
    # Percentual de AA por Nota e Região
    st.markdown("### Percentual de Programas com AA (Nota x Região)")
    
    # Criar tabela de percentual
    df_aa_nota_regiao = df_filtrado[df_filtrado['Status AA'] == 'Com Editais AA']
    crosstab_aa = pd.crosstab(df_aa_nota_regiao['Região'], df_aa_nota_regiao['NOTA'])
    crosstab_aa = crosstab_aa.reindex(columns=colunas_ordenadas, fill_value=0)
    
    # Calcular percentuais
    perc_aa_nota_regiao = (crosstab_aa / crosstab_nota_regiao * 100).fillna(0).round(1)
    
    fig_heat_perc = go.Figure(data=go.Heatmap(
        z=perc_aa_nota_regiao.values,
        x=perc_aa_nota_regiao.columns,
        y=perc_aa_nota_regiao.index,
        texttemplate='%{z:.1f}%',
        textfont={"size": 11},
        colorscale='RdYlGn',
        colorbar=dict(title="% com AA")
    ))
    
    fig_heat_perc.update_layout(
        title='Percentual de Programas com AA por Nota e Região',
        xaxis_title='Nota CAPES',
        yaxis_title='Região',
        height=400
    )
    st.plotly_chart(fig_heat_perc, use_container_width=True)

st.markdown("---")

# Análise: Tipo IES x Modalidade
st.markdown("## 🏛️ Cruzamento: Tipo de IES x Modalidade de Ensino")

if 'Tipo de IES' in df_filtrado.columns and 'Modalidade de Ensino' in df_filtrado.columns:
    crosstab_ies_mod = pd.crosstab(
        df_filtrado['Tipo de IES'],
        df_filtrado['Modalidade de Ensino']
    )
    
    col_heat2, col_table2 = st.columns([2, 1])
    
    with col_heat2:
        fig_heat_ies = go.Figure(data=go.Heatmap(
            z=crosstab_ies_mod.values,
            x=crosstab_ies_mod.columns,
            y=crosstab_ies_mod.index,
            texttemplate='%{z}',
            textfont={"size": 12},
            colorscale='Blues',
            colorbar=dict(title="Programas")
        ))
        
        fig_heat_ies.update_layout(
            title='Distribuição: Tipo de IES x Modalidade',
            xaxis_title='Modalidade de Ensino',
            yaxis_title='Tipo de IES',
            height=400
        )
        st.plotly_chart(fig_heat_ies, use_container_width=True)
    
    with col_table2:
        st.markdown("**Tabela de Frequência:**")
        st.dataframe(crosstab_ies_mod, use_container_width=True, height=400)
    
    # Percentual com AA
    st.markdown("### Percentual com AA (Tipo IES x Modalidade)")
    
    df_aa_ies = df_filtrado[df_filtrado['Status AA'] == 'Com Editais AA']
    crosstab_aa_ies = pd.crosstab(df_aa_ies['Tipo de IES'], df_aa_ies['Modalidade de Ensino'])
    perc_aa_ies = (crosstab_aa_ies / crosstab_ies_mod * 100).fillna(0).round(1)
    
    fig_heat_perc_ies = go.Figure(data=go.Heatmap(
        z=perc_aa_ies.values,
        x=perc_aa_ies.columns,
        y=perc_aa_ies.index,
        texttemplate='%{z:.1f}%',
        textfont={"size": 11},
        colorscale='RdYlGn',
        colorbar=dict(title="% com AA")
    ))
    
    fig_heat_perc_ies.update_layout(
        title='Percentual com AA: Tipo de IES x Modalidade',
        xaxis_title='Modalidade de Ensino',
        yaxis_title='Tipo de IES',
        height=400
    )
    st.plotly_chart(fig_heat_perc_ies, use_container_width=True)

st.markdown("---")

# Análise de Concentração
st.markdown("## 📍 Análise de Concentração")

tab1, tab2, tab3 = st.tabs(["Por Região", "Por Nota", "Por Tipo de IES"])

with tab1:
    st.markdown("### Concentração de AA por Região")
    
    if 'Região' in df_filtrado.columns:
        # Calcular estatísticas por região
        stats_regiao = df_filtrado.groupby('Região').agg({
            'Tem_AA': ['sum', 'count', 'mean'],
            'Vagas Totais AA': 'sum'
        }).reset_index()
        
        stats_regiao.columns = ['Região', 'Com_AA', 'Total', 'Perc_AA', 'Vagas_AA']
        stats_regiao['Perc_AA'] = (stats_regiao['Perc_AA'] * 100).round(1)
        stats_regiao = stats_regiao.sort_values('Com_AA', ascending=False)
        
        col_conc1, col_conc2 = st.columns(2)
        
        with col_conc1:
            # Gráfico de bolhas
            fig_bubble = px.scatter(
                stats_regiao,
                x='Total',
                y='Com_AA',
                size='Vagas_AA',
                color='Perc_AA',
                text='Região',
                title='Concentração de AA por Região',
                labels={
                    'Total': 'Total de Programas',
                    'Com_AA': 'Programas com AA',
                    'Perc_AA': '% com AA',
                    'Vagas_AA': 'Vagas AA'
                },
                color_continuous_scale='Viridis'
            )
            fig_bubble.update_traces(textposition='top center')
            fig_bubble.update_layout(height=400)
            st.plotly_chart(fig_bubble, use_container_width=True)
        
        with col_conc2:
            st.markdown("**Dados de Concentração:**")
            st.dataframe(
                stats_regiao[['Região', 'Total', 'Com_AA', 'Perc_AA', 'Vagas_AA']],
                use_container_width=True,
                hide_index=True
            )

with tab2:
    st.markdown("### Concentração de AA por Nota CAPES")
    
    if 'NOTA' in df_filtrado.columns:
        stats_nota = df_filtrado.groupby('NOTA').agg({
            'Tem_AA': ['sum', 'count', 'mean'],
            'Vagas Totais AA': 'sum'
        }).reset_index()
        
        stats_nota.columns = ['Nota', 'Com_AA', 'Total', 'Perc_AA', 'Vagas_AA']
        stats_nota['Perc_AA'] = (stats_nota['Perc_AA'] * 100).round(1)
        
        # Ordenar por ordem de notas
        stats_nota['Nota'] = pd.Categorical(stats_nota['Nota'], categories=ORDEM_NOTAS, ordered=True)
        stats_nota = stats_nota.sort_values('Nota')
        
        col_nota1, col_nota2 = st.columns(2)
        
        with col_nota1:
            fig_nota_conc = go.Figure()
            
            fig_nota_conc.add_trace(go.Bar(
                name='Total de Programas',
                x=stats_nota['Nota'],
                y=stats_nota['Total'],
                marker_color=CORES['primaria'],
                yaxis='y',
                offsetgroup=1
            ))
            
            fig_nota_conc.add_trace(go.Scatter(
                name='% com AA',
                x=stats_nota['Nota'],
                y=stats_nota['Perc_AA'],
                marker_color=CORES['com_aa'],
                yaxis='y2',
                mode='lines+markers',
                line=dict(width=3)
            ))
            
            fig_nota_conc.update_layout(
                title='AA por Nota CAPES',
                xaxis_title='Nota',
                yaxis=dict(title='Total de Programas', side='left'),
                yaxis2=dict(title='% com AA', overlaying='y', side='right'),
                height=400,
                hovermode='x unified'
            )
            st.plotly_chart(fig_nota_conc, use_container_width=True)
        
        with col_nota2:
            st.markdown("**Dados por Nota:**")
            st.dataframe(
                stats_nota[['Nota', 'Total', 'Com_AA', 'Perc_AA', 'Vagas_AA']],
                use_container_width=True,
                hide_index=True
            )

with tab3:
    st.markdown("### Concentração de AA por Tipo de IES")
    
    if 'Tipo de IES' in df_filtrado.columns:
        stats_ies = df_filtrado.groupby('Tipo de IES').agg({
            'Tem_AA': ['sum', 'count', 'mean'],
            'Vagas Totais AA': 'sum'
        }).reset_index()
        
        stats_ies.columns = ['Tipo_IES', 'Com_AA', 'Total', 'Perc_AA', 'Vagas_AA']
        stats_ies['Perc_AA'] = (stats_ies['Perc_AA'] * 100).round(1)
        stats_ies = stats_ies.sort_values('Perc_AA', ascending=False)
        
        col_ies1, col_ies2 = st.columns(2)
        
        with col_ies1:
            fig_ies_conc = px.bar(
                stats_ies,
                x='Tipo_IES',
                y=['Total', 'Com_AA'],
                title='Programas por Tipo de IES',
                labels={'value': 'Quantidade', 'Tipo_IES': 'Tipo de IES'},
                barmode='group',
                color_discrete_sequence=[CORES['primaria'], CORES['com_aa']]
            )
            fig_ies_conc.update_layout(height=400)
            st.plotly_chart(fig_ies_conc, use_container_width=True)
        
        with col_ies2:
            st.markdown("**Dados por Tipo IES:**")
            st.dataframe(
                stats_ies[['Tipo_IES', 'Total', 'Com_AA', 'Perc_AA', 'Vagas_AA']],
                use_container_width=True,
                hide_index=True
            )

st.markdown("---")

# Matriz de Correlação
st.markdown("## 🔢 Matriz de Correlação - Variáveis Numéricas")

# Selecionar colunas numéricas disponíveis
colunas_para_correlacao = []
colunas_possiveis = {
    'Qnt. Vagas Totais': 'Vagas Totais',
    'Vagas Totais AA': 'Vagas AA',
    'Vagas Totais Agregadas': 'Vagas Agregadas',
    'Vagas Totais Por Grupo/Exclusivas': 'Vagas Por Grupo',
    'Tem_AA': 'Tem AA (0/1)'
}

df_corr = df_filtrado.copy()
colunas_disponiveis = {}

for col_orig, col_nome in colunas_possiveis.items():
    if col_orig in df_corr.columns:
        colunas_disponiveis[col_nome] = col_orig

if len(colunas_disponiveis) >= 2:
    # Criar DataFrame apenas com colunas numéricas
    df_numeric = df_corr[[col for col in colunas_disponiveis.values()]].copy()
    df_numeric.columns = list(colunas_disponiveis.keys())
    
    # Calcular correlação
    corr_matrix = df_numeric.corr()
    
    # Heatmap de correlação
    fig_corr = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=corr_matrix.columns,
        y=corr_matrix.columns,
        texttemplate='%{z:.2f}',
        textfont={"size": 11},
        colorscale='RdBu',
        zmid=0,
        colorbar=dict(title="Correlação")
    ))
    
    fig_corr.update_layout(
        title='Matriz de Correlação entre Variáveis',
        height=500
    )
    st.plotly_chart(fig_corr, use_container_width=True)
    
    st.info("""
    **Interpretação:**
    - Valores próximos a **+1**: Correlação positiva forte
    - Valores próximos a **0**: Sem correlação
    - Valores próximos a **-1**: Correlação negativa forte
    """)
else:
    st.warning("Dados insuficientes para análise de correlação.")

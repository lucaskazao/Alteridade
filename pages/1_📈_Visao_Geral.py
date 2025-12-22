"""
📈 Visão Geral - Análises Detalhadas
Página de análises por Nota, Região, Modalidade e Tipo de IES
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.data_loader import load_all_areas, get_data_for_area, prepare_dataframe
from utils.filters import render_area_selector, render_global_filters
from config import ORDEM_NOTAS, CORES

# Configuração da página
st.set_page_config(
    page_title="Visão Geral | Dashboard AA",
    page_icon="📈",
    layout="wide"
)

# Carregar dados
areas_data, df_todas_areas, lista_areas = load_all_areas()

# Sidebar
st.sidebar.markdown("# 📈 Visão Geral")
st.sidebar.markdown("Análises detalhadas por dimensão")
st.sidebar.markdown("---")

# Seletor de Área
area_selecionada = render_area_selector(lista_areas)

# Obter dados
df = get_data_for_area(area_selecionada, areas_data, df_todas_areas)
df = prepare_dataframe(df)

# Filtros
df_filtrado, filtros_ativos = render_global_filters(df)

# ==================== CONTEÚDO ====================

st.title("📈 Visão Geral - Análises Detalhadas")
st.markdown("Análise da presença de ações afirmativas por diferentes dimensões")
st.markdown("---")

# Análises por Nota e Região
st.markdown("## 📊 Análise por Nota e Região")

col_nota, col_regiao = st.columns(2)

with col_nota:
    # Gráfico: Nota x Presença de AA
    nota_aa = pd.crosstab(df_filtrado['NOTA'], df_filtrado['Status AA'])
    
    # Ordenar notas
    notas_existentes = [nota for nota in ORDEM_NOTAS if nota in nota_aa.index]
    notas_extras = [nota for nota in nota_aa.index if nota not in ORDEM_NOTAS]
    notas_existentes.extend(sorted(notas_extras))
    nota_aa = nota_aa.reindex(notas_existentes, fill_value=0)
    
    # Criar gráfico
    fig_nota = go.Figure()
    
    com_aa_values = nota_aa['Com Editais AA'].tolist() if 'Com Editais AA' in nota_aa.columns else [0] * len(notas_existentes)
    sem_aa_values = nota_aa['Sem Editais AA'].tolist() if 'Sem Editais AA' in nota_aa.columns else [0] * len(notas_existentes)
    
    fig_nota.add_trace(go.Bar(
        name='Com Editais AA',
        x=notas_existentes,
        y=com_aa_values,
        marker_color=CORES['com_aa']
    ))
    fig_nota.add_trace(go.Bar(
        name='Sem Editais AA',
        x=notas_existentes,
        y=sem_aa_values,
        marker_color=CORES['sem_aa']
    ))
    
    fig_nota.update_layout(
        title='Presença de AA por Nota do Programa',
        xaxis_title='Nota',
        yaxis_title='Quantidade de Programas',
        barmode='stack',
        xaxis_type='category',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=400
    )
    st.plotly_chart(fig_nota, use_container_width=True)
    
    # Tabela resumo - Nota
    st.markdown("**Tabela Resumo - Por Nota:**")
    nota_resumo = nota_aa.copy()
    nota_resumo['Total'] = nota_resumo.sum(axis=1)
    if 'Com Editais AA' in nota_resumo.columns:
        nota_resumo['% Com AA'] = (nota_resumo['Com Editais AA'] / nota_resumo['Total'] * 100).round(1)
    if 'Sem Editais AA' in nota_resumo.columns:
        nota_resumo['% Sem AA'] = (nota_resumo['Sem Editais AA'] / nota_resumo['Total'] * 100).round(1)
    
    st.dataframe(nota_resumo, use_container_width=True)

with col_regiao:
    # Gráfico: Região x Presença de AA
    regiao_aa = pd.crosstab(df_filtrado['Região'], df_filtrado['Status AA'])
    
    fig_regiao = go.Figure()
    fig_regiao.add_trace(go.Bar(
        name='Com Editais AA',
        x=regiao_aa.index,
        y=regiao_aa['Com Editais AA'] if 'Com Editais AA' in regiao_aa.columns else [],
        marker_color=CORES['com_aa']
    ))
    fig_regiao.add_trace(go.Bar(
        name='Sem Editais AA',
        x=regiao_aa.index,
        y=regiao_aa['Sem Editais AA'] if 'Sem Editais AA' in regiao_aa.columns else [],
        marker_color=CORES['sem_aa']
    ))
    
    fig_regiao.update_layout(
        title='Presença de AA por Região',
        xaxis_title='Região',
        yaxis_title='Quantidade de Programas',
        barmode='stack',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=400
    )
    st.plotly_chart(fig_regiao, use_container_width=True)
    
    # Tabela resumo - Região
    st.markdown("**Tabela Resumo - Por Região:**")
    regiao_resumo = regiao_aa.copy()
    regiao_resumo['Total'] = regiao_resumo.sum(axis=1)
    if 'Com Editais AA' in regiao_resumo.columns:
        regiao_resumo['% Com AA'] = (regiao_resumo['Com Editais AA'] / regiao_resumo['Total'] * 100).round(1)
    if 'Sem Editais AA' in regiao_resumo.columns:
        regiao_resumo['% Sem AA'] = (regiao_resumo['Sem Editais AA'] / regiao_resumo['Total'] * 100).round(1)
    
    st.dataframe(regiao_resumo, use_container_width=True)

st.markdown("---")

# Segunda linha de gráficos
st.markdown("## 📊 Análise por Modalidade e Tipo de IES")

col_modalidade, col_ies = st.columns(2)

with col_modalidade:
    # Gráfico: Modalidade de Ensino x Presença de AA
    modalidade_aa = pd.crosstab(df_filtrado['Modalidade de Ensino'], df_filtrado['Status AA'])
    
    fig_modalidade = go.Figure()
    fig_modalidade.add_trace(go.Bar(
        name='Com Editais AA',
        x=modalidade_aa.index,
        y=modalidade_aa['Com Editais AA'] if 'Com Editais AA' in modalidade_aa.columns else [],
        marker_color=CORES['com_aa']
    ))
    fig_modalidade.add_trace(go.Bar(
        name='Sem Editais AA',
        x=modalidade_aa.index,
        y=modalidade_aa['Sem Editais AA'] if 'Sem Editais AA' in modalidade_aa.columns else [],
        marker_color=CORES['sem_aa']
    ))
    
    fig_modalidade.update_layout(
        title='Presença de AA por Modalidade de Ensino',
        xaxis_title='Modalidade de Ensino',
        yaxis_title='Quantidade de Programas',
        barmode='stack',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=400
    )
    st.plotly_chart(fig_modalidade, use_container_width=True)
    
    # Tabela resumo
    st.markdown("**Tabela Resumo - Por Modalidade:**")
    modalidade_resumo = modalidade_aa.copy()
    modalidade_resumo['Total'] = modalidade_resumo.sum(axis=1)
    if 'Com Editais AA' in modalidade_resumo.columns:
        modalidade_resumo['% Com AA'] = (modalidade_resumo['Com Editais AA'] / modalidade_resumo['Total'] * 100).round(1)
    
    st.dataframe(modalidade_resumo, use_container_width=True)

with col_ies:
    # Gráfico: Tipo de IES x Presença de AA
    ies_aa = pd.crosstab(df_filtrado['Tipo de IES'], df_filtrado['Status AA'])
    
    fig_ies = go.Figure()
    fig_ies.add_trace(go.Bar(
        name='Com Editais AA',
        x=ies_aa.index,
        y=ies_aa['Com Editais AA'] if 'Com Editais AA' in ies_aa.columns else [],
        marker_color=CORES['com_aa']
    ))
    fig_ies.add_trace(go.Bar(
        name='Sem Editais AA',
        x=ies_aa.index,
        y=ies_aa['Sem Editais AA'] if 'Sem Editais AA' in ies_aa.columns else [],
        marker_color=CORES['sem_aa']
    ))
    
    fig_ies.update_layout(
        title='Presença de AA por Tipo de IES',
        xaxis_title='Tipo de IES',
        yaxis_title='Quantidade de Programas',
        barmode='stack',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=400
    )
    st.plotly_chart(fig_ies, use_container_width=True)
    
    # Tabela resumo
    st.markdown("**Tabela Resumo - Por Tipo de IES:**")
    ies_resumo = ies_aa.copy()
    ies_resumo['Total'] = ies_resumo.sum(axis=1)
    if 'Com Editais AA' in ies_resumo.columns:
        ies_resumo['% Com AA'] = (ies_resumo['Com Editais AA'] / ies_resumo['Total'] * 100).round(1)
    
    st.dataframe(ies_resumo, use_container_width=True)

st.markdown("---")

# Análise de Tipo de AA
st.markdown("## 🎯 Análise por Tipo de Ação Afirmativa")

col_aa_tipo, col_aa_tabela = st.columns([1, 1])

with col_aa_tipo:
    # Preparar dados
    aa_tipo_data = {
        'AA Agregada - Sim': (df_filtrado['AA Agregada'].str.upper() == 'SIM').sum(),
        'AA Agregada - Não': len(df_filtrado) - (df_filtrado['AA Agregada'].str.upper() == 'SIM').sum(),
        'AA Por Grupo - Sim': (df_filtrado['AA Por Grupo'].str.upper() == 'SIM').sum(),
        'AA Por Grupo - Não': len(df_filtrado) - (df_filtrado['AA Por Grupo'].str.upper() == 'SIM').sum()
    }
    
    # Gráfico de barras comparativo
    fig_aa_tipo = go.Figure()
    
    fig_aa_tipo.add_trace(go.Bar(
        name='Sim',
        x=['AA Agregada', 'AA Por Grupo'],
        y=[aa_tipo_data['AA Agregada - Sim'], aa_tipo_data['AA Por Grupo - Sim']],
        marker_color=CORES['com_aa'],
        text=[aa_tipo_data['AA Agregada - Sim'], aa_tipo_data['AA Por Grupo - Sim']],
        textposition='auto'
    ))
    
    fig_aa_tipo.add_trace(go.Bar(
        name='Não',
        x=['AA Agregada', 'AA Por Grupo'],
        y=[aa_tipo_data['AA Agregada - Não'], aa_tipo_data['AA Por Grupo - Não']],
        marker_color=CORES['sem_aa'],
        text=[aa_tipo_data['AA Agregada - Não'], aa_tipo_data['AA Por Grupo - Não']],
        textposition='auto'
    ))
    
    fig_aa_tipo.update_layout(
        title='Comparação: AA Agregada vs AA Por Grupo',
        xaxis_title='Tipo de AA',
        yaxis_title='Quantidade de Programas',
        barmode='stack',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=400
    )
    st.plotly_chart(fig_aa_tipo, use_container_width=True)

with col_aa_tabela:
    st.markdown("**Tabela Resumo - Tipo de AA:**")
    
    # Criar dataframe resumo
    aa_resumo_data = []
    
    total_agregada = aa_tipo_data['AA Agregada - Sim'] + aa_tipo_data['AA Agregada - Não']
    aa_resumo_data.append({
        'Tipo': 'AA Agregada',
        'Sim': aa_tipo_data['AA Agregada - Sim'],
        '% Sim': round((aa_tipo_data['AA Agregada - Sim'] / total_agregada * 100) if total_agregada > 0 else 0, 1),
        'Não': aa_tipo_data['AA Agregada - Não'],
        'Total': total_agregada
    })
    
    total_grupo = aa_tipo_data['AA Por Grupo - Sim'] + aa_tipo_data['AA Por Grupo - Não']
    aa_resumo_data.append({
        'Tipo': 'AA Por Grupo',
        'Sim': aa_tipo_data['AA Por Grupo - Sim'],
        '% Sim': round((aa_tipo_data['AA Por Grupo - Sim'] / total_grupo * 100) if total_grupo > 0 else 0, 1),
        'Não': aa_tipo_data['AA Por Grupo - Não'],
        'Total': total_grupo
    })
    
    df_aa_resumo = pd.DataFrame(aa_resumo_data)
    df_aa_resumo = df_aa_resumo.set_index('Tipo')
    
    st.dataframe(df_aa_resumo, use_container_width=True)
    
    st.info("""
    **Legenda:**
    - **AA Agregada**: Vagas destinadas a múltiplos grupos sem especificação individual
    - **AA Por Grupo**: Vagas destinadas especificamente para cada grupo
    """)

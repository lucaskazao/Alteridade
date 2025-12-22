"""
Sistema de filtros compartilhado para todas as páginas
"""
import streamlit as st
import pandas as pd
from config import GRUPOS_SOCIAIS, ORDEM_NOTAS


def render_area_selector(lista_areas):
    """
    Render seletor de área na sidebar
    
    Args:
        lista_areas: lista de nomes das áreas
        
    Returns:
        str: área selecionada
    """
    st.sidebar.header("🎯 Seleção de Área")
    area_selecionada = st.sidebar.selectbox(
        'Selecione a área de análise:',
        options=['Todas as Áreas'] + lista_areas,
        index=0
    )
    
    # Mostrar info
    if area_selecionada == 'Todas as Áreas':
        st.sidebar.info(f"📊 Analisando **todas as {len(lista_areas)} áreas**")
    else:
        st.sidebar.success(f"📌 Área: **{area_selecionada}**")
    
    return area_selecionada


def render_global_filters(df):
    """
    Renderiza filtros globais na sidebar
    
    Args:
        df: DataFrame com dados
        
    Returns:
        tuple: (df_filtrado, filtros_ativos)
    """
    st.sidebar.markdown("---")
    st.sidebar.header("🔍 Filtros")
    
    filtros_ativos = 0
    df_filtrado = df.copy()
    
    # Filtros Geográficos
    st.sidebar.markdown("### 📍 Localização")
    
    if 'Região' in df.columns:
        regioes_disponiveis = sorted(df['Região'].dropna().unique().tolist())
        regioes_selecionadas = st.sidebar.multiselect(
            "Região:",
            options=regioes_disponiveis,
            default=[],
            key='regiao_filter'
        )
        if regioes_selecionadas:
            df_filtrado = df_filtrado[df_filtrado['Região'].isin(regioes_selecionadas)]
            filtros_ativos += 1
    
    if 'UF' in df.columns:
        ufs_disponiveis = sorted([str(uf) for uf in df['UF'].dropna().unique().tolist()])
        ufs_selecionadas = st.sidebar.multiselect(
            "UF:",
            options=ufs_disponiveis,
            default=[],
            key='uf_filter'
        )
        if ufs_selecionadas:
            df_filtrado = df_filtrado[df_filtrado['UF'].isin(ufs_selecionadas)]
            filtros_ativos += 1
    
    # Filtros de Avaliação
    st.sidebar.markdown("### ⭐ Avaliação")
    
    if 'NOTA' in df.columns:
        notas_existentes = [n for n in ORDEM_NOTAS if n in df['NOTA'].unique()]
        notas_selecionadas = st.sidebar.multiselect(
            "Nota CAPES:",
            options=notas_existentes,
            default=[],
            key='nota_filter'
        )
        if notas_selecionadas:
            df_filtrado = df_filtrado[df_filtrado['NOTA'].isin(notas_selecionadas)]
            filtros_ativos += 1
    
    # Filtros Institucionais
    st.sidebar.markdown("### 🏛️ Instituição")
    
    if 'Tipo de IES' in df.columns:
        tipos_ies = sorted(df['Tipo de IES'].dropna().unique().tolist())
        tipos_selecionados = st.sidebar.multiselect(
            "Tipo de IES:",
            options=tipos_ies,
            default=[],
            key='tipo_ies_filter'
        )
        if tipos_selecionados:
            df_filtrado = df_filtrado[df_filtrado['Tipo de IES'].isin(tipos_selecionados)]
            filtros_ativos += 1
    
    if 'Modalidade de Ensino' in df.columns:
        modalidades = sorted(df['Modalidade de Ensino'].dropna().unique().tolist())
        modalidades_selecionadas = st.sidebar.multiselect(
            "Modalidade de Ensino:",
            options=modalidades,
            default=[],
            key='modalidade_filter'
        )
        if modalidades_selecionadas:
            df_filtrado = df_filtrado[df_filtrado['Modalidade de Ensino'].isin(modalidades_selecionadas)]
            filtros_ativos += 1
    
    # Filtros de AA
    st.sidebar.markdown("### 🎯 Ações Afirmativas")
    
    status_aa_filtro = st.sidebar.radio(
        "Status:",
        options=['Todos', 'Com AA', 'Sem AA'],
        index=0,
        key='status_aa_filter'
    )
    if status_aa_filtro == 'Com AA':
        df_filtrado = df_filtrado[df_filtrado['Status AA'] == 'Com Editais AA']
        filtros_ativos += 1
    elif status_aa_filtro == 'Sem AA':
        df_filtrado = df_filtrado[df_filtrado['Status AA'] == 'Sem Editais AA']
        filtros_ativos += 1
    
    # Botão limpar filtros
    st.sidebar.markdown("---")
    if st.sidebar.button("🔄 Limpar Todos os Filtros", use_container_width=True):
        keys_to_clear = [
            'regiao_filter', 'uf_filter', 'nota_filter',
            'tipo_ies_filter', 'modalidade_filter', 'status_aa_filter'
        ]
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()
    
    # Mostrar contador
    if filtros_ativos > 0:
        st.sidebar.success(f"✅ {filtros_ativos} filtro(s) ativo(s)")
        st.sidebar.info(f"📊 Mostrando **{len(df_filtrado)}** de **{len(df)}** programas")
    else:
        st.sidebar.info(f"📊 Mostrando **{len(df)}** programas")
    
    return df_filtrado, filtros_ativos

"""
🗺️ Distribuição Geográfica
Análise espacial dos programas e ações afirmativas
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.data_loader import load_all_areas, get_data_for_area, prepare_dataframe
from utils.filters import render_area_selector, render_global_filters
from config import CORES

# Coordenadas dos Estados Brasileiros (Centro aproximado)
COORDENADAS_UFS = {
    'AC': (-8.77, -70.55), 'AL': (-9.62, -36.82), 'AM': (-3.47, -65.10),
    'AP': (1.41, -51.77), 'BA': (-13.29, -41.71), 'CE': (-5.20, -39.53),
    'DF': (-15.83, -47.86), 'ES': (-19.19, -40.34), 'GO': (-15.98, -49.86),
    'MA': (-5.42, -45.44), 'MG': (-18.10, -44.38), 'MS': (-20.51, -54.54),
    'MT': (-12.64, -55.42), 'PA': (-3.79, -52.48), 'PB': (-7.28, -36.72),
    'PE': (-8.38, -37.86), 'PI': (-6.60, -42.28), 'PR': (-24.89, -51.55),
    'RJ': (-22.25, -42.66), 'RN': (-5.81, -36.59), 'RO': (-10.83, -63.34),
    'RR': (1.99, -61.33), 'RS': (-30.17, -53.50), 'SC': (-27.45, -50.95),
    'SE': (-10.57, -37.45), 'SP': (-22.19, -48.79), 'TO': (-9.46, -48.26)
}

# Configuração da página
st.set_page_config(
    page_title="Geografia | Dashboard AA",
    page_icon="🗺️",
    layout="wide"
)

# Carregar dados
areas_data, df_todas_areas, lista_areas = load_all_areas()

# Sidebar
st.sidebar.markdown("# 🗺️ Geografia")
st.sidebar.markdown("Distribuição espacial dos programas")
st.sidebar.markdown("---")

# Seletor de Área
area_selecionada = render_area_selector(lista_areas)

# Obter dados
df = get_data_for_area(area_selecionada, areas_data, df_todas_areas)
df = prepare_dataframe(df)

# Filtros
df_filtrado, filtros_ativos = render_global_filters(df)

# ==================== CONTEÚDO ====================

st.title("🗺️ Distribuição Geográfica")
st.markdown("Análise da distribuição espacial dos programas de pós-graduação e políticas de ações afirmativas.")
st.markdown("---")

# Preparar dados geográficos
if 'UF' in df_filtrado.columns:
    # Agrupar por UF
    uf_stats = df_filtrado.groupby('UF').agg({
        'Nome do Programa': 'count',
        'Status AA': lambda x: (x == 'Com Editais AA').sum()
    }).reset_index()
    
    uf_stats.columns = ['UF', 'Total Programas', 'Com AA']
    uf_stats['% Com AA'] = (uf_stats['Com AA'] / uf_stats['Total Programas'] * 100).round(1)
    
    # Adicionar coordenadas
    uf_stats['lat'] = uf_stats['UF'].map(lambda x: COORDENADAS_UFS.get(x, (0,0))[0])
    uf_stats['lon'] = uf_stats['UF'].map(lambda x: COORDENADAS_UFS.get(x, (0,0))[1])
    
    # Adicionar nome da Região (pegando do df original)
    # Garantir que temos apenas uma região por UF para o mapeamento
    uf_regiao = df_filtrado[['UF', 'Região']].dropna().drop_duplicates(subset=['UF']).set_index('UF')
    uf_stats['Região'] = uf_stats['UF'].map(uf_regiao['Região'])

    # --- Mapa ---
    st.markdown("## 📍 Mapa de Distribuição")
    
    col_map1, col_map2 = st.columns([3, 1])
    
    with col_map1:
        # Mapa de Bolhas (Colorido por % AA)
        fig_map = px.scatter_geo(
            uf_stats,
            lat='lat',
            lon='lon',
            size='Total Programas',
            color='% Com AA',
            hover_name='UF',
            hover_data=['Total Programas', 'Com AA', '% Com AA', 'Região'],
            scope='south america',
            title='Distribuição por Estado (Tamanho = Qtd. Programas | Cor = % com AA)',
            projection='mercator',
            color_continuous_scale='Viridis',
            size_max=50
        )
        
        fig_map.update_traces(marker=dict(line=dict(width=1, color='black')))
        
        fig_map.update_geos(
            visible=False, resolution=50,
            showcountries=True, countrycolor="RebeccaPurple",
            showcoastlines=True, coastlinecolor="RebeccaPurple",
            showland=True, landcolor="#E5ECF6",
            fitbounds="locations"
        )
        
        fig_map.update_layout(height=600, margin={"r":0,"t":30,"l":0,"b":0})
        st.plotly_chart(fig_map, use_container_width=True)
        
    with col_map2:
        # Métricas rápidas
        st.markdown("### Destaques")
        
        top_uf = uf_stats.sort_values('Total Programas', ascending=False).iloc[0]
        st.metric("Maior Concentração", f"{top_uf['UF']}", f"{top_uf['Total Programas']} progs")
        
        top_aa = uf_stats.sort_values('% Com AA', ascending=False).iloc[0]
        st.metric("Maior % AA", f"{top_aa['UF']}", f"{top_aa['% Com AA']}%")
        
        st.markdown("---")
        st.markdown("**Legenda:**")
        st.info("• Tamanho: Volume de programas\n• Cor: Intensidade de Ações Afirmativas (Roxo = Menor, Amarelo = Maior)")

    st.markdown("---")

    # --- Análise Regional ---
    st.markdown("## 🏙️ Análise Regional")
    
    col_reg1, col_reg2 = st.columns(2)
    
    with col_reg1:
        # Barras: Total vs Com AA por Região
        regiao_stats = df_filtrado.groupby('Região')['Status AA'].value_counts().unstack(fill_value=0)
        
        fig_reg = go.Figure()
        fig_reg.add_trace(go.Bar(
            name='Com AA',
            x=regiao_stats.index,
            y=regiao_stats.get('Com Editais AA', []),
            marker_color=CORES['com_aa'],
            text=regiao_stats.get('Com Editais AA', []),
            textposition='auto'
        ))
        fig_reg.add_trace(go.Bar(
            name='Sem AA',
            x=regiao_stats.index,
            y=regiao_stats.get('Sem Editais AA', []),
            marker_color=CORES['sem_aa'],
            text=regiao_stats.get('Sem Editais AA', []),
            textposition='auto'
        ))
        
        fig_reg.update_layout(
            title='Programas por Região (Com vs Sem AA)',
            barmode='group',
            xaxis_title='Região',
            yaxis_title='Quantidade',
            legend=dict(orientation="h", y=1.1)
        )
        st.plotly_chart(fig_reg, use_container_width=True)
        
    with col_reg2:
        # Pizza: Distribuição do Total de Programas por Região
        total_por_regiao = df_filtrado['Região'].value_counts()
        
        fig_pie_reg = px.pie(
            values=total_por_regiao.values,
            names=total_por_regiao.index,
            title='Distribuição Total de Programas por Região',
            hole=0.4
        )
        fig_pie_reg.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_pie_reg, use_container_width=True)

    st.markdown("---")

    # --- Análise por Estado (Detalhada) ---
    st.markdown("## 🏛️ Detalhamento por Estado (UF)")
    
    col_uf1, col_uf2 = st.columns([2, 1])
    
    # Ordenar por total de programas
    uf_stats_sorted = uf_stats.sort_values('Total Programas', ascending=False)
    
    with col_uf1:
        # Gráfico de Barras com % de AA (Eixo duplo ou cor)
        fig_uf = go.Figure()
        
        fig_uf.add_trace(go.Bar(
            x=uf_stats_sorted['UF'],
            y=uf_stats_sorted['Total Programas'],
            name='Total de Programas',
            marker_color=CORES['primaria'],
            yaxis='y'
        ))
        
        fig_uf.add_trace(go.Scatter(
            x=uf_stats_sorted['UF'],
            y=uf_stats_sorted['% Com AA'],
            name='% Com AA',
            mode='lines+markers',
            marker=dict(color=CORES['secundaria'], size=8),
            line=dict(width=3),
            yaxis='y2'
        ))
        
        fig_uf.update_layout(
            title='Total de Programas e Percentual de Ações Afirmativas por UF',
            xaxis_title='Estado (UF)',
            yaxis=dict(title='Total de Programas'),
            yaxis2=dict(
                title='% Com AA',
                overlaying='y',
                side='right',
                range=[0, 100]
            ),
            legend=dict(orientation="h", y=1.1),
            height=500
        )
        
        st.plotly_chart(fig_uf, use_container_width=True)
    
    with col_uf2:
        st.markdown("### Tabela Detalhada")
        st.dataframe(
            uf_stats_sorted[['UF', 'Região', 'Total Programas', 'Com AA', '% Com AA']],
            use_container_width=True,
            hide_index=True,
            height=450
        )

    # --- Interseção Geografia x Grupos ---
    st.markdown("---")
    st.markdown("## 🗺️ x 👥 Interseção: Geografia e Grupos Sociais")
    st.markdown("Quais grupos são mais contemplados em cada região?")
    
    from config import GRUPOS_SOCIAIS
    
    # Preparar dados para Heatmap
    # Linhas: Regiões, Colunas: Grupos, Valores: % de programas da região que atendem o grupo
    
    heatmap_data = []
    regioes_unicas = sorted(df_filtrado['Região'].dropna().unique())
    
    for regiao in regioes_unicas:
        df_reg = df_filtrado[df_filtrado['Região'] == regiao]
        total_progs_reg = len(df_reg)
        
        if total_progs_reg > 0:
            row_data = {'Região': regiao}
            for nome_grupo, col_db in GRUPOS_SOCIAIS.items():
                if col_db in df_reg.columns:
                    qtd = (df_reg[col_db].fillna('').str.strip().str.upper() == 'SIM').sum()
                    perc = (qtd / total_progs_reg) * 100
                    row_data[nome_grupo] = perc
            heatmap_data.append(row_data)
            
    if heatmap_data:
        df_heatmap = pd.DataFrame(heatmap_data).set_index('Região')
        
        fig_heat = px.imshow(
            df_heatmap,
            labels=dict(x="Grupo Social", y="Região", color="% de Adesão"),
            x=df_heatmap.columns,
            y=df_heatmap.index,
            color_continuous_scale='Blues',
            text_auto='.1f',
            aspect="auto"
        )
        fig_heat.update_layout(
            title="Percentual de Programas que Contemplam cada Grupo (por Região)",
            height=400
        )
        st.plotly_chart(fig_heat, use_container_width=True)
    else:
        st.info("Dados insuficientes para gerar o mapa de calor.")
    
    # --- Treemap Hierárquico ---
    st.markdown("---")
    st.markdown("## 🌳 Visão Hierárquica")
    st.markdown("Distribuição: Região > UF > IES")
    
    if 'Sigla da IES' in df_filtrado.columns:
        # Preparar dados para treemap
        # Agrupar para contar programas por IES
        treemap_data = df_filtrado.groupby(['Região', 'UF', 'Sigla da IES']).size().reset_index(name='Contagem')
        
        fig_tree = px.treemap(
            treemap_data,
            path=[px.Constant("Brasil"), 'Região', 'UF', 'Sigla da IES'],
            values='Contagem',
            color='Região',
            title='Hierarquia de Programas (Tamanho = Qtd. Programas)',
            color_discrete_sequence=px.colors.qualitative.Prism
        )
        fig_tree.update_layout(height=600)
        st.plotly_chart(fig_tree, use_container_width=True)

else:
    st.warning("Dados geográficos (UF/Região) não disponíveis para a visualização.")

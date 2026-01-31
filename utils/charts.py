"""
Funções de visualização compartilhadas
"""
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from config import CORES, ORDEM_NOTAS


def find_column(df, pattern):
    """
    Encontra coluna no DataFrame que corresponde ao padrão (case-insensitive, ignorando espaços)
    
    Args:
        df: DataFrame
        pattern: padrão a procurar (ex: 'TIPODEIES', 'EDITAISAA')
        
    Returns:
        str: nome da coluna ou None se não encontrar
    """
    pattern_normalized = pattern.upper().replace(' ', '')
    for col in df.columns:
        if col.upper().replace(' ', '') == pattern_normalized:
            return col
    return None


def create_bar_chart(df, x, y, color=None, title="", orientation='v', barmode='group'):
    """
    Cria gráfico de barras
    
    Args:
        df: DataFrame
        x: coluna para eixo X
        y: coluna para eixo Y  
        color: coluna para cores
        title: título do gráfico
        orientation: 'v' ou 'h' 
        barmode: 'group', 'stack', 'relative'
        
    Returns:
        plotly figure
    """
    fig = px.bar(
        df, 
        x=x, 
        y=y, 
        color=color,
        title=title,
        orientation=orientation,
        barmode=barmode
    )
    return fig


def create_scatter_plot(df, x, y, color=None, size=None, title="", trendline=None):
    """
    Cria scatter plot
    
    Args:
        df: DataFrame
        x: coluna para eixo X
        y: coluna para eixo Y
        color: coluna para cores
        size: coluna para tamanho dos pontos
        title: título do gráfico
        trendline: 'ols', 'lowess', None
        
    Returns:
        plotly figure
    """
    fig = px.scatter(
        df,
        x=x,
        y=y,
        color=color,
        size=size,
        title=title,
        trendline=trendline
    )
    return fig


def create_heatmap(data, x_labels=None, y_labels=None, title="", colorscale='RdYlGn'):
    """
    Cria heatmap
    
    Args:
        data: matriz de dados
        x_labels: labels do eixo X
        y_labels: labels do eixo Y
        title: título do gráfico
        colorscale: escala de cores
        
    Returns:
        plotly figure
    """
    fig = go.Figure(data=go.Heatmap(
        z=data,
        x=x_labels,
        y=y_labels,
        colorscale=colorscale,
        text=data,
        texttemplate='%{text:.1f}',
        textfont={"size": 10}
    ))
    
    fig.update_layout(title=title)
    return fig


def create_pie_chart(values, names, title="", hole=0.4):
    """
    Cria gráfico de pizza/donut
    
    Args:
        values: valores
        names: nomes das fatias
        title: título
        hole: tamanho do buraco (0-1), 0 = pizza, >0 = donut
        
    Returns:
        plotly figure
    """
    fig = px.pie(
        values=values,
        names=names,
        title=title,
        hole=hole
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    return fig


def create_boxplot(df, x, y, color=None, title=""):
    """
    Cria boxplot
    
    Args:
        df: DataFrame
        x: coluna categórica
        y: coluna numérica
        color: coluna para cores
        title: título
        
    Returns:
        plotly figure
    """
    fig = px.box(
        df,
        x=x,
        y=y,
        color=color,
        title=title
    )
    return fig


def create_correlation_matrix(df, columns):
    """
    Cria matriz de correlação
    
    Args:
        df: DataFrame
        columns: lista de colunas para incluir
        
    Returns:
        plotly figure
    """
    corr_matrix = df[columns].corr()
    
    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=corr_matrix.columns,
        y=corr_matrix.columns,
        colorscale='RdBu',
        zmid=0,
        text=corr_matrix.values,
        texttemplate='%{text:.2f}',
        textfont={"size": 10}
    ))
    
    fig.update_layout(
        title="Matriz de Correlação",
        xaxis_title="",
        yaxis_title=""
    )
    
    return fig


def create_radar_chart(categories, values_dict, title=""):
    """
    Cria radar/spider chart
    
    Args:
        categories: lista de categorias
        values_dict: dict com {nome: [valores]}
        title: título
        
    Returns:
        plotly figure
    """
    fig = go.Figure()
    
    for name, values in values_dict.items():
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name=name
        ))
    
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True)),
        title=title,
        showlegend=True
    )
    
    return fig


def create_ies_type_aa_chart(df, title="Universidades Públicas/Privadas com Ações Afirmativas", include_invalid=True):
    """
    Cria gráfico de barras com universidades privadas/públicas e ações afirmativas
    
    Args:
        df: DataFrame com dados de programas
        title: título do gráfico
        include_invalid: Se True, inclui registros com dados faltantes/inválidos
        
    Returns:
        plotly figure, crosstab, info_dict
    """
    # Encontrar colunas de Tipo de IES e Editais AA (com suporte a múltiplas variações)
    df_clean = df.copy()
    
    tipo_ies_col = find_column(df_clean, 'TIPODEIES')
    editais_col = find_column(df_clean, 'EDITAISAA')
    
    if tipo_ies_col is None or editais_col is None:
        raise ValueError("Colunas 'Tipo de IES' ou 'Editais AA' não encontradas no DataFrame")
    
    # Normalizar valores de Tipo de IES
    df_clean['Tipo_IES_Limpo'] = df_clean[tipo_ies_col].fillna('').astype(str).str.strip().str.upper()
    
    # Padronizar para 'Pública' e 'Privada'
    df_clean['Tipo_Classificado'] = df_clean['Tipo_IES_Limpo'].apply(
        lambda x: 'Pública' if x == 'PUBLICA' else ('Privada' if x == 'PRIVADA' else 'Dados Faltantes/Inválidos')
    )
    
    # Normalizar valores de Editais AA
    df_clean['Editais_AA_Limpo'] = df_clean[editais_col].fillna('').astype(str).str.strip().str.upper()
    df_clean['Tem AA'] = df_clean['Editais_AA_Limpo'].apply(
        lambda x: 'Com AA' if x == 'SIM' else ('Sem AA' if x in ['NAO', 'NÃO'] else 'Dados Faltantes/Inválidos')
    )
    
    if include_invalid:
        # Incluir todos os registros
        df_filtrado = df_clean.copy()
    else:
        # Remover registros com dados faltantes
        df_filtrado = df_clean[(df_clean['Tipo_Classificado'] != 'Dados Faltantes/Inválidos') & 
                               (df_clean['Tem AA'] != 'Dados Faltantes/Inválidos')]
    
    # Criar crosstab
    crosstab = pd.crosstab(df_filtrado['Tipo_Classificado'], df_filtrado['Tem AA'])
    
    # Criar gráfico
    fig = go.Figure()
    
    # Ordem de exibição
    ordem_aa = ['Com AA', 'Sem AA', 'Dados Faltantes/Inválidos']
    
    # Adicionar barras para cada tipo de AA
    for aa_type in ordem_aa:
        if aa_type in crosstab.columns:
            valores = crosstab[aa_type]
            
            # Determinar cor
            if aa_type == 'Com AA':
                cor = CORES['com_aa']
            elif aa_type == 'Sem AA':
                cor = CORES['sem_aa']
            else:
                cor = CORES['neutra']
            
            fig.add_trace(go.Bar(
                x=valores.index,
                y=valores.values,
                name=aa_type,
                marker=dict(color=cor)
            ))
    
    fig.update_layout(
        title=title,
        xaxis_title='Tipo de IES',
        yaxis_title='Quantidade de Programas',
        barmode='group',
        hovermode='x unified',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=500
    )
    
    # Info sobre dados
    info_dict = {
        'total': len(df_clean),
        'com_dados': len(df_filtrado),
        'sem_dados': len(df_clean) - len(df_filtrado),
        'pública_com_aa': crosstab.loc['Pública', 'Com AA'] if ('Pública' in crosstab.index and 'Com AA' in crosstab.columns) else 0,
        'pública_sem_aa': crosstab.loc['Pública', 'Sem AA'] if ('Pública' in crosstab.index and 'Sem AA' in crosstab.columns) else 0,
        'privada_com_aa': crosstab.loc['Privada', 'Com AA'] if ('Privada' in crosstab.index and 'Com AA' in crosstab.columns) else 0,
        'privada_sem_aa': crosstab.loc['Privada', 'Sem AA'] if ('Privada' in crosstab.index and 'Sem AA' in crosstab.columns) else 0,
    }
    
    return fig, crosstab, info_dict

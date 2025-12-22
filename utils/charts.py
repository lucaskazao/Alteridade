"""
Funções de visualização compartilhadas
"""
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from config import CORES, ORDEM_NOTAS


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

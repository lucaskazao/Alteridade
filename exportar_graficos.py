"""
Script para exportar todos os gráficos das páginas:
- Análise de Vagas
- Grupos Sociais  
- Distribuição Geográfica

Para todas as áreas do conhecimento.
"""
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from config import GRUPOS_SOCIAIS, CORES, ORDEM_NOTAS

def criar_estrutura_pastas(pasta_base):
    """Cria a estrutura de pastas para armazenar os gráficos"""
    pasta_base = Path(pasta_base)
    pasta_base.mkdir(exist_ok=True)
    return pasta_base

def normalizar_nome_arquivo(nome):
    """Normaliza nome para usar em arquivo"""
    return nome.replace(' ', '_').replace('/', '_').replace('\\', '_').lower()

def gerar_graficos_analise_vagas(df, area_nome, pasta_destino):
    """Gera todos os gráficos da página Análise de Vagas"""
    print(f"  Gerando gráficos de Análise de Vagas para {area_nome}...")
    
    pasta_vagas = pasta_destino / "analise_vagas"
    pasta_vagas.mkdir(exist_ok=True, parents=True)
    
    # Converter colunas de vagas para numérico
    for col in ['Qnt Vagas Totais', 'Vagas Totais AA', 'Vagas Totais Agregadas', 'Vagas Totais Por Grupo/Exclusivas']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    # Calcular totais
    total_vagas_gerais = df['Qnt Vagas Totais'].sum()
    total_vagas_aa = df['Vagas Totais AA'].sum()
    total_vagas_agregadas = df['Vagas Totais Agregadas'].sum()
    total_vagas_por_grupo = df['Vagas Totais Por Grupo/Exclusivas'].sum()
    
    # 1. Gráfico de barras comparativo
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
        title=f'Distribuição Total de Vagas por Categoria - {area_nome}',
        xaxis_title='Categoria de Vagas',
        yaxis_title='Quantidade de Vagas',
        showlegend=False,
        height=400,
        width=800
    )
    fig_vagas.write_image(pasta_vagas / "comparacao_categorias_barras.png")
    
    # 2. Gráfico de pizza - Proporção
    if total_vagas_gerais > 0:
        fig_prop = px.pie(
            values=[total_vagas_aa, total_vagas_gerais - total_vagas_aa],
            names=['Vagas AA', 'Ampla Concorrência'],
            color_discrete_sequence=[CORES['com_aa'], CORES['neutra']],
            hole=0.4,
            title=f'Proporção de Vagas AA - {area_nome}'
        )
        fig_prop.update_traces(textposition='inside', textinfo='percent+label')
        fig_prop.update_layout(height=400, width=600)
        fig_prop.write_image(pasta_vagas / "comparacao_categorias_pizza.png")
    
    # 3. Distribuição por Região
    if 'Regi�o' in df.columns:
        vagas_por_regiao = df.groupby('Regi�o').agg({
            'Qnt Vagas Totais': 'sum',
            'Vagas Totais AA': 'sum',
            'Vagas Totais Agregadas': 'sum',
            'Vagas Totais Por Grupo/Exclusivas': 'sum'
        }).reset_index()
        
        fig_regiao = go.Figure()
        fig_regiao.add_trace(go.Bar(
            name='Vagas AA',
            x=vagas_por_regiao['Regi�o'],
            y=vagas_por_regiao['Vagas Totais AA'],
            marker_color=CORES['com_aa']
        ))
        fig_regiao.add_trace(go.Bar(
            name='Ampla Concorrência',
            x=vagas_por_regiao['Regi�o'],
            y=vagas_por_regiao['Qnt Vagas Totais'] - vagas_por_regiao['Vagas Totais AA'],
            marker_color=CORES['neutra']
        ))
        fig_regiao.update_layout(
            title=f'Vagas por Região (AA vs Ampla Concorrência) - {area_nome}',
            xaxis_title='Região',
            yaxis_title='Quantidade de Vagas',
            barmode='stack',
            height=400,
            width=900
        )
        fig_regiao.write_image(pasta_vagas / "distribuicao_regiao.png")
    
    # 4. Distribuição por Nota CAPES
    if 'Nota' in df.columns:
        vagas_por_nota = df.groupby('Nota').agg({
            'Qnt Vagas Totais': 'sum',
            'Vagas Totais AA': 'sum'
        }).reset_index()
        
        vagas_por_nota['Nota'] = pd.Categorical(vagas_por_nota['Nota'], categories=ORDEM_NOTAS, ordered=True)
        vagas_por_nota = vagas_por_nota.sort_values('Nota')
        
        # Gráfico de linhas
        fig_nota = go.Figure()
        fig_nota.add_trace(go.Scatter(
            x=vagas_por_nota['Nota'],
            y=vagas_por_nota['Qnt Vagas Totais'],
            mode='lines+markers',
            name='Vagas Totais',
            line=dict(color=CORES['primaria'], width=3),
            marker=dict(size=10)
        ))
        fig_nota.add_trace(go.Scatter(
            x=vagas_por_nota['Nota'],
            y=vagas_por_nota['Vagas Totais AA'],
            mode='lines+markers',
            name='Vagas AA',
            line=dict(color=CORES['com_aa'], width=3),
            marker=dict(size=10)
        ))
        fig_nota.update_layout(
            title=f'Vagas por Nota CAPES - {area_nome}',
            xaxis_title='Nota',
            yaxis_title='Quantidade de Vagas',
            height=400,
            width=800
        )
        fig_nota.write_image(pasta_vagas / "distribuicao_nota_linhas.png")
        
        # Percentual de vagas AA por nota
        vagas_por_nota['% AA'] = (
            vagas_por_nota['Vagas Totais AA'] / vagas_por_nota['Qnt Vagas Totais'] * 100
        ).round(1)
        
        fig_perc = px.bar(
            vagas_por_nota,
            x='Nota',
            y='% AA',
            title=f'Percentual de Vagas AA por Nota - {area_nome}',
            text='% AA',
            color='% AA',
            color_continuous_scale='Viridis'
        )
        fig_perc.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig_perc.update_layout(showlegend=False, height=400, width=700)
        fig_perc.write_image(pasta_vagas / "distribuicao_nota_percentual.png")
    
    # 5. Análise de Médias
    df_com_aa = df[df['Status AA'] == 'Com Editais AA']
    df_sem_aa = df[df['Status AA'] == 'Sem Editais AA']
    
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
        title=f'Média de Vagas Totais por Status AA - {area_nome}',
        yaxis_title='Média de Vagas',
        showlegend=False,
        height=400,
        width=600
    )
    fig_media_status.write_image(pasta_vagas / "media_status_aa.png")
    
    # Média por Região
    if 'Regi�o' in df.columns:
        media_por_regiao = df.groupby('Regi�o')['Qnt Vagas Totais'].mean().sort_values(ascending=False)
        
        fig_media_regiao = px.bar(
            x=media_por_regiao.index,
            y=media_por_regiao.values,
            title=f'Média de Vagas por Região - {area_nome}',
            labels={'x': 'Região', 'y': 'Média de Vagas'},
            text=media_por_regiao.values
        )
        fig_media_regiao.update_traces(texttemplate='%{text:.1f}', textposition='outside', marker_color=CORES['primaria'])
        fig_media_regiao.update_layout(showlegend=False, height=400, width=700)
        fig_media_regiao.write_image(pasta_vagas / "media_regiao.png")
    
    # Média por Tipo de IES
    if 'Tipo de IES' in df.columns:
        media_por_ies = df.groupby('Tipo de IES')['Qnt Vagas Totais'].mean().sort_values(ascending=False)
        
        fig_media_ies = px.bar(
            x=media_por_ies.index,
            y=media_por_ies.values,
            title=f'Média de Vagas por Tipo IES - {area_nome}',
            labels={'x': 'Tipo de IES', 'y': 'Média de Vagas'},
            text=media_por_ies.values
        )
        fig_media_ies.update_traces(texttemplate='%{text:.1f}', textposition='outside', marker_color=CORES['secundaria'])
        fig_media_ies.update_layout(showlegend=False, height=400, width=700)
        fig_media_ies.write_image(pasta_vagas / "media_tipo_ies.png")
    
    # 6. Top Programas
    df_top_aa = df[df['Vagas Totais AA'] > 0].nlargest(10, 'Vagas Totais AA')
    
    if len(df_top_aa) > 0:
        fig_top = px.bar(
            df_top_aa,
            y='Nome do Programa',
            x='Vagas Totais AA',
            orientation='h',
            title=f'Top 10 Programas - Mais Vagas AA - {area_nome}',
            text='Vagas Totais AA',
            color='Vagas Totais AA',
            color_continuous_scale='Viridis'
        )
        fig_top.update_traces(textposition='outside')
        fig_top.update_layout(yaxis={'categoryorder':'total ascending'}, height=600, width=900, showlegend=False)
        fig_top.write_image(pasta_vagas / "top_10_programas.png")
    
    print(f"    [OK] Graficos de Analise de Vagas salvos em: {pasta_vagas}")

def gerar_graficos_grupos_sociais(df, area_nome, pasta_destino):
    """Gera todos os gráficos da página Grupos Sociais"""
    print(f"  Gerando gráficos de Grupos Sociais para {area_nome}...")
    
    pasta_grupos = pasta_destino / "grupos_sociais"
    pasta_grupos.mkdir(exist_ok=True, parents=True)
    
    # Preparar dados de grupos
    grupos_stats = []
    
    for nome_grupo, coluna in GRUPOS_SOCIAIS.items():
        if coluna in df.columns:
            programas_com_grupo = (df[coluna].fillna('').str.strip().str.upper() == 'SIM').sum()
            
            coluna_vagas = f"Vagas {coluna.replace('AA ', '')}"
            if coluna_vagas in df.columns:
                total_vagas = pd.to_numeric(df[coluna_vagas], errors='coerce').fillna(0).sum()
            else:
                total_vagas = 0
            
            grupos_stats.append({
                'Grupo': nome_grupo,
                'Programas': int(programas_com_grupo),
                'Vagas': int(total_vagas),
                '% Programas': round((programas_com_grupo / len(df) * 100), 1) if len(df) > 0 else 0
            })
    
    df_grupos = pd.DataFrame(grupos_stats).sort_values('Programas', ascending=False)
    
    # 1. Visão Geral - Gráfico de barras
    fig_bar = px.bar(
        df_grupos,
        x='Grupo',
        y='Programas',
        title=f'Número de Programas que Contemplam Cada Grupo - {area_nome}',
        text='Programas',
        color='Programas',
        color_continuous_scale='Viridis'
    )
    fig_bar.update_traces(textposition='outside')
    fig_bar.update_layout(
        xaxis_title='Grupo Social',
        yaxis_title='Quantidade de Programas',
        showlegend=False,
        height=500,
        width=1000
    )
    fig_bar.write_image(pasta_grupos / "visao_geral_grupos.png")
    
    # 2. Pizza - Distribuição de Programas
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
        title=f'Distribuição de Programas por Grupo - {area_nome}',
        hole=0.4
    )
    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
    fig_pie.update_layout(height=500, width=700)
    fig_pie.write_image(pasta_grupos / "distribuicao_programas_pizza.png")
    
    # 3. Treemap - Distribuição de Vagas
    df_vagas = df_grupos[df_grupos['Vagas'] > 0]
    
    if not df_vagas.empty:
        fig_tree = px.treemap(
            df_vagas,
            path=['Grupo'],
            values='Vagas',
            title=f'Distribuição de Vagas por Grupo (Treemap) - {area_nome}',
            color='Vagas',
            color_continuous_scale='Greens'
        )
        fig_tree.update_layout(height=500, width=800)
        fig_tree.write_image(pasta_grupos / "distribuicao_vagas_treemap.png")
    
    # 4. Radar - Perfil Regional
    if 'Regi�o' in df.columns:
        regioes = sorted(df['Regi�o'].dropna().unique())
        grupos_radar = df_grupos['Grupo'].tolist()
        
        fig_radar = go.Figure()
        
        for regiao in regioes:
            df_reg = df[df['Regi�o'] == regiao]
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
            height=600,
            width=900,
            title=f"Percentual de Programas por Região que Contemplam cada Grupo - {area_nome}"
        )
        fig_radar.write_image(pasta_grupos / "perfil_regional_radar.png")
    
    # 5. Múltiplos Grupos
    grupos_por_programa = []
    
    for idx, row in df.iterrows():
        grupos_contemplados = []
        for nome_grupo, coluna in GRUPOS_SOCIAIS.items():
            if coluna in df.columns:
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
        quant_groups = df_multiplos['Quantidade'].value_counts().sort_index()
        
        fig_multi = px.bar(
            x=quant_groups.index,
            y=quant_groups.values,
            title=f'Distribuição de Programas por Nº de Grupos - {area_nome}',
            labels={'x': 'Quantidade de Grupos', 'y': 'Quantidade de Programas'},
            text=quant_groups.values
        )
        fig_multi.update_traces(textposition='outside', marker_color=CORES['terciaria'])
        fig_multi.update_layout(showlegend=False, height=500, width=700)
        fig_multi.write_image(pasta_grupos / "multiplos_grupos.png")
    
    # 6. Interseccionalidade por Área (apenas para "Todas as Áreas")
    if 'Área' in df.columns and area_nome == "Todas as Áreas":
        data_area = []
        
        for idx, row in df.iterrows():
            count_grupos = 0
            for _, col in GRUPOS_SOCIAIS.items():
                if col in df.columns:
                    if str(row[col]).strip().upper() == 'SIM':
                        count_grupos += 1
            
            data_area.append({
                'Área': row['Área'],
                'Qtd Grupos': count_grupos
            })
        
        if data_area:
            df_area_groups = pd.DataFrame(data_area)
            area_stats = df_area_groups.groupby('Área')['Qtd Grupos'].mean().reset_index()
            area_stats = area_stats.sort_values('Qtd Grupos', ascending=False)
            area_stats.columns = ['Área', 'Média de Grupos por Programa']
            
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
            fig_area.update_layout(height=600, width=1200)
            fig_area.write_image(pasta_grupos / "interseccionalidade_area.png")
    
    # 7. Análise detalhada por grupo
    pasta_por_grupo = pasta_grupos / "por_grupo"
    pasta_por_grupo.mkdir(exist_ok=True, parents=True)
    
    for grupo in df_grupos['Grupo'].tolist():
        coluna_grupo = GRUPOS_SOCIAIS[grupo]
        df_grupo = df[df[coluna_grupo].fillna('').str.strip().str.upper() == 'SIM'].copy()
        
        if len(df_grupo) > 0:
            grupo_normalizado = normalizar_nome_arquivo(grupo)
            
            # Distribuição por Região
            if 'Regi�o' in df_grupo.columns:
                regiao_counts = df_grupo['Regi�o'].value_counts()
                
                fig_regiao = px.bar(
                    x=regiao_counts.index,
                    y=regiao_counts.values,
                    title=f'Distribuição Geográfica - {grupo}',
                    labels={'x': 'Região', 'y': 'Quantidade de Programas'},
                    text=regiao_counts.values
                )
                fig_regiao.update_traces(textposition='outside', marker_color=CORES['primaria'])
                fig_regiao.update_layout(showlegend=False, height=400, width=700)
                fig_regiao.write_image(pasta_por_grupo / f"{grupo_normalizado}_regiao.png")
            
            # Distribuição por Nota
            if 'Nota' in df_grupo.columns:
                nota_counts = df_grupo['Nota'].value_counts()
                
                fig_nota = px.bar(
                    x=nota_counts.index,
                    y=nota_counts.values,
                    title=f'Distribuição por Nota CAPES - {grupo}',
                    labels={'x': 'Nota', 'y': 'Quantidade de Programas'},
                    text=nota_counts.values
                )
                fig_nota.update_traces(textposition='outside', marker_color=CORES['secundaria'])
                fig_nota.update_layout(showlegend=False, height=400, width=700)
                fig_nota.write_image(pasta_por_grupo / f"{grupo_normalizado}_nota.png")
    
    print(f"    [OK] Graficos de Grupos Sociais salvos em: {pasta_grupos}")

def gerar_graficos_distribuicao_geografica(df, area_nome, pasta_destino):
    """Gera todos os gráficos da página Distribuição Geográfica"""
    print(f"  Gerando gráficos de Distribuição Geográfica para {area_nome}...")
    
    pasta_geo = pasta_destino / "distribuicao_geografica"
    pasta_geo.mkdir(exist_ok=True, parents=True)
    
    # Coordenadas dos Estados Brasileiros
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
    
    if 'UF' not in df.columns:
        print(f"    ⚠ Dados geográficos não disponíveis para {area_nome}")
        return
    
    # Preparar dados geográficos
    uf_stats = df.groupby('UF').agg({
        'Nome do Programa': 'count',
        'Status AA': lambda x: (x == 'Com Editais AA').sum()
    }).reset_index()
    
    uf_stats.columns = ['UF', 'Total Programas', 'Com AA']
    uf_stats['% Com AA'] = (uf_stats['Com AA'] / uf_stats['Total Programas'] * 100).round(1)
    
    # Adicionar coordenadas
    uf_stats['lat'] = uf_stats['UF'].map(lambda x: COORDENADAS_UFS.get(x, (0,0))[0])
    uf_stats['lon'] = uf_stats['UF'].map(lambda x: COORDENADAS_UFS.get(x, (0,0))[1])
    
    # Adicionar região
    if 'Região' in df.columns:
        uf_regiao = df[['UF', 'Região']].dropna().drop_duplicates(subset=['UF']).set_index('UF')
        uf_stats['Região'] = uf_stats['UF'].map(uf_regiao['Região'])
    
    # 1. Mapa de Distribuição
    fig_map = px.scatter_geo(
        uf_stats,
        lat='lat',
        lon='lon',
        size='Total Programas',
        color='% Com AA',
        hover_name='UF',
        hover_data=['Total Programas', 'Com AA', '% Com AA', 'Região'] if 'Região' in uf_stats.columns else ['Total Programas', 'Com AA', '% Com AA'],
        scope='south america',
        title=f'Distribuição por Estado - {area_nome}',
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
    fig_map.update_layout(height=600, width=1000, margin={"r":0,"t":30,"l":0,"b":0})
    fig_map.write_image(pasta_geo / "mapa_distribuicao.png")
    
    # 2. Análise Regional
    if 'Regi�o' in df.columns:
        # Barras: Total vs Com AA por Região
        regiao_stats = df.groupby('Regi�o')['Status AA'].value_counts().unstack(fill_value=0)
        
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
            title=f'Programas por Região (Com vs Sem AA) - {area_nome}',
            barmode='group',
            xaxis_title='Região',
            yaxis_title='Quantidade',
            legend=dict(orientation="h", y=1.1),
            height=500,
            width=900
        )
        fig_reg.write_image(pasta_geo / "analise_regional_barras.png")
        
        # Pizza: Distribuição Total por Região
        total_por_regiao = df['Regi�o'].value_counts()
        
        fig_pie_reg = px.pie(
            values=total_por_regiao.values,
            names=total_por_regiao.index,
            title=f'Distribuição Total de Programas por Região - {area_nome}',
            hole=0.4
        )
        fig_pie_reg.update_traces(textposition='inside', textinfo='percent+label')
        fig_pie_reg.update_layout(height=500, width=700)
        fig_pie_reg.write_image(pasta_geo / "analise_regional_pizza.png")
    
    # 3. Detalhamento por UF
    uf_stats_sorted = uf_stats.sort_values('Total Programas', ascending=False)
    
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
        title=f'Total de Programas e Percentual de AA por UF - {area_nome}',
        xaxis_title='Estado (UF)',
        yaxis=dict(title='Total de Programas'),
        yaxis2=dict(
            title='% Com AA',
            overlaying='y',
            side='right',
            range=[0, 100]
        ),
        legend=dict(orientation="h", y=1.1),
        height=500,
        width=1200
    )
    fig_uf.write_image(pasta_geo / "detalhamento_uf.png")
    
    # 4. Heatmap: Geografia x Grupos Sociais
    if 'Regi�o' in df.columns:
        heatmap_data = []
        regioes_unicas = sorted(df['Regi�o'].dropna().unique())
        
        for regiao in regioes_unicas:
            df_reg = df[df['Regi�o'] == regiao]
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
                title=f"Percentual de Programas que Contemplam cada Grupo (por Região) - {area_nome}",
                height=500,
                width=1000
            )
            fig_heat.write_image(pasta_geo / "heatmap_grupos_regiao.png")
    
    # 5. Treemap Hierárquico
    if 'Sigla da IES' in df.columns and 'Regi�o' in df.columns:
        treemap_data = df.groupby(['Regi�o', 'UF', 'Sigla da IES']).size().reset_index(name='Contagem')
        
        fig_tree = px.treemap(
            treemap_data,
            path=[px.Constant("Brasil"), 'Regi�o', 'UF', 'Sigla da IES'],
            values='Contagem',
            color='Regi�o',
            title=f'Hierarquia de Programas (Região > UF > IES) - {area_nome}',
            color_discrete_sequence=px.colors.qualitative.Prism
        )
        fig_tree.update_layout(height=700, width=1200)
        fig_tree.write_image(pasta_geo / "treemap_hierarquico.png")
    
    print(f"    [OK] Graficos de Distribuicao Geografica salvos em: {pasta_geo}")

def main():
    """Função principal"""
    print("=" * 80)
    print("EXPORTAÇÃO DE GRÁFICOS - ANÁLISE DE VAGAS E GRUPOS SOCIAIS")
    print("=" * 80)
    print()
    
    # Carregar dados
    print("Carregando dados...")
    excel_file = pd.ExcelFile('dados_brutos.xlsx')
    areas_data = {}
    
    for sheet_name in excel_file.sheet_names:
        df_area = pd.read_excel(excel_file, sheet_name=sheet_name)
        
        # Pular planilhas que não têm as colunas necessárias
        if 'Editais AA' not in df_area.columns or 'Nome do Programa' not in df_area.columns:
            print(f"  [SKIP] Pulando planilha '{sheet_name}' - colunas necessarias nao encontradas")
            continue
        
        df_area['Área'] = sheet_name
        if 'Nota' in df_area.columns:
            df_area['Nota'] = df_area['Nota'].astype(str).str.strip()
        # Adicionar Status AA
        df_area['Status AA'] = df_area['Editais AA'].apply(
            lambda x: 'Com Editais AA' if str(x).upper() == 'SIM' else 'Sem Editais AA'
        )
        areas_data[sheet_name] = df_area
    
    df_todas_areas = pd.concat(areas_data.values(), ignore_index=True)
    
    print(f"[OK] Dados carregados: {len(areas_data)} areas encontradas")
    print()
    
    # Criar pasta base
    pasta_base = criar_estrutura_pastas("graficos_exportados")
    print(f"[OK] Pasta base criada: {pasta_base.absolute()}")
    print()
    
    # Processar "Todas as Áreas"
    print("Processando: Todas as Áreas")
    pasta_todas = pasta_base / "Todas_as_Areas"
    pasta_todas.mkdir(exist_ok=True, parents=True)
    
    gerar_graficos_analise_vagas(df_todas_areas.copy(), "Todas as Áreas", pasta_todas)
    gerar_graficos_grupos_sociais(df_todas_areas.copy(), "Todas as Áreas", pasta_todas)
    gerar_graficos_distribuicao_geografica(df_todas_areas.copy(), "Todas as Áreas", pasta_todas)
    print()
    
    # Processar cada área individual
    for area_nome, df_area in areas_data.items():
        print(f"Processando: {area_nome}")
        pasta_area = pasta_base / normalizar_nome_arquivo(area_nome)
        pasta_area.mkdir(exist_ok=True, parents=True)
        
        gerar_graficos_analise_vagas(df_area.copy(), area_nome, pasta_area)
        gerar_graficos_grupos_sociais(df_area.copy(), area_nome, pasta_area)
        gerar_graficos_distribuicao_geografica(df_area.copy(), area_nome, pasta_area)
        print()
    
    # Resumo final
    print("=" * 80)
    print("EXPORTAÇÃO CONCLUÍDA COM SUCESSO!")
    print("=" * 80)
    print()
    print(f"📁 Pasta de destino: {pasta_base.absolute()}")
    print(f"📊 Áreas processadas: {len(areas_data) + 1} (incluindo 'Todas as Áreas')")
    print()
    print("Estrutura de pastas criada:")
    print(f"  └── graficos_exportados/")
    print(f"      ├── Todas_as_Areas/")
    print(f"      │   ├── analise_vagas/")
    print(f"      │   ├── grupos_sociais/")
    print(f"      │   └── distribuicao_geografica/")
    for area_nome in areas_data.keys():
        area_norm = normalizar_nome_arquivo(area_nome)
        print(f"      ├── {area_norm}/")
        print(f"      │   ├── analise_vagas/")
        print(f"      │   ├── grupos_sociais/")
        print(f"      │   └── distribuicao_geografica/")
    print()

if __name__ == "__main__":
    main()

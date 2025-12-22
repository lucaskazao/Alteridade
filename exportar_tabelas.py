"""
Script para exportar todas as tabelas de dados que geram os gráficos das páginas:
- Análise de Vagas
- Grupos Sociais  
- Distribuição Geográfica

Para todas as áreas do conhecimento.
As tabelas são exportadas em formato CSV e Excel.
"""
import os
import pandas as pd
from pathlib import Path
from config import GRUPOS_SOCIAIS, ORDEM_NOTAS

def criar_estrutura_pastas(pasta_base):
    """Cria a estrutura de pastas para armazenar as tabelas"""
    pasta_base = Path(pasta_base)
    pasta_base.mkdir(exist_ok=True)
    return pasta_base

def normalizar_nome_arquivo(nome):
    """Normaliza nome para usar em arquivo"""
    return nome.replace(' ', '_').replace('/', '_').replace('\\', '_').lower()

def salvar_tabela(df, pasta, nome_arquivo):
    """Salva uma tabela em formato CSV e Excel"""
    # Salvar como CSV
    csv_path = pasta / f"{nome_arquivo}.csv"
    df.to_csv(csv_path, index=False, encoding='utf-8-sig')
    
    # Salvar como Excel
    excel_path = pasta / f"{nome_arquivo}.xlsx"
    df.to_excel(excel_path, index=False, engine='openpyxl')
    
    return csv_path, excel_path

def exportar_tabelas_analise_vagas(df, area_nome, pasta_destino):
    """Exporta todas as tabelas da página Análise de Vagas"""
    print(f"  Exportando tabelas de Análise de Vagas para {area_nome}...")
    
    pasta_vagas = pasta_destino / "analise_vagas"
    pasta_vagas.mkdir(exist_ok=True, parents=True)
    
    # Converter colunas de vagas para numérico
    for col in ['Qnt Vagas Totais', 'Vagas Totais AA', 'Vagas Totais Agregadas', 'Vagas Totais Por Grupo/Exclusivas']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    # 1. Resumo Geral de Vagas
    total_vagas_gerais = df['Qnt Vagas Totais'].sum()
    total_vagas_aa = df['Vagas Totais AA'].sum()
    total_vagas_agregadas = df['Vagas Totais Agregadas'].sum()
    total_vagas_por_grupo = df['Vagas Totais Por Grupo/Exclusivas'].sum()
    
    resumo_geral = pd.DataFrame({
        'Categoria': ['Vagas Totais', 'Vagas AA (Total)', 'Vagas Agregadas', 'Vagas Por Grupo'],
        'Quantidade': [total_vagas_gerais, total_vagas_aa, total_vagas_agregadas, total_vagas_por_grupo],
        'Percentual do Total': [
            100.0,
            (total_vagas_aa / total_vagas_gerais * 100) if total_vagas_gerais > 0 else 0,
            (total_vagas_agregadas / total_vagas_gerais * 100) if total_vagas_gerais > 0 else 0,
            (total_vagas_por_grupo / total_vagas_gerais * 100) if total_vagas_gerais > 0 else 0
        ]
    })
    resumo_geral['Percentual do Total'] = resumo_geral['Percentual do Total'].round(2)
    salvar_tabela(resumo_geral, pasta_vagas, "resumo_geral_vagas")
    
    # 2. Proporção AA vs Ampla Concorrência
    if total_vagas_gerais > 0:
        proporcao = pd.DataFrame({
            'Tipo': ['Vagas AA', 'Ampla Concorrência'],
            'Quantidade': [total_vagas_aa, total_vagas_gerais - total_vagas_aa],
            'Percentual': [
                (total_vagas_aa / total_vagas_gerais * 100),
                ((total_vagas_gerais - total_vagas_aa) / total_vagas_gerais * 100)
            ]
        })
        proporcao['Percentual'] = proporcao['Percentual'].round(2)
        salvar_tabela(proporcao, pasta_vagas, "proporcao_aa_ampla")
    
    # 3. Distribuição por Região
    if 'Região' in df.columns:
        vagas_por_regiao = df.groupby('Região').agg({
            'Qnt Vagas Totais': 'sum',
            'Vagas Totais AA': 'sum',
            'Vagas Totais Agregadas': 'sum',
            'Vagas Totais Por Grupo/Exclusivas': 'sum',
            'Nome do Programa': 'count'
        }).reset_index()
        
        vagas_por_regiao.columns = ['Região', 'Total Vagas', 'Vagas AA', 'Vagas Agregadas', 
                                     'Vagas Por Grupo', 'Qtd Programas']
        vagas_por_regiao['% AA'] = (vagas_por_regiao['Vagas AA'] / vagas_por_regiao['Total Vagas'] * 100).round(2)
        vagas_por_regiao['Ampla Concorrência'] = vagas_por_regiao['Total Vagas'] - vagas_por_regiao['Vagas AA']
        
        vagas_por_regiao = vagas_por_regiao.sort_values('Total Vagas', ascending=False)
        salvar_tabela(vagas_por_regiao, pasta_vagas, "distribuicao_regiao")
    
    # 4. Distribuição por Nota CAPES
    if 'Nota' in df.columns:
        vagas_por_nota = df.groupby('Nota').agg({
            'Qnt Vagas Totais': 'sum',
            'Vagas Totais AA': 'sum',
            'Vagas Totais Agregadas': 'sum',
            'Vagas Totais Por Grupo/Exclusivas': 'sum',
            'Nome do Programa': 'count'
        }).reset_index()
        
        vagas_por_nota.columns = ['Nota', 'Total Vagas', 'Vagas AA', 'Vagas Agregadas', 
                                  'Vagas Por Grupo', 'Qtd Programas']
        vagas_por_nota['% AA'] = (vagas_por_nota['Vagas AA'] / vagas_por_nota['Total Vagas'] * 100).round(2)
        vagas_por_nota['Ampla Concorrência'] = vagas_por_nota['Total Vagas'] - vagas_por_nota['Vagas AA']
        
        # Ordenar por nota
        vagas_por_nota['Nota'] = pd.Categorical(vagas_por_nota['Nota'], categories=ORDEM_NOTAS, ordered=True)
        vagas_por_nota = vagas_por_nota.sort_values('Nota')
        salvar_tabela(vagas_por_nota, pasta_vagas, "distribuicao_nota")
    
    # 5. Análise de Médias por Status AA
    df_com_aa = df[df['Status AA'] == 'Com Editais AA']
    df_sem_aa = df[df['Status AA'] == 'Sem Editais AA']
    
    media_status = pd.DataFrame({
        'Status': ['Com AA', 'Sem AA'],
        'Qtd Programas': [len(df_com_aa), len(df_sem_aa)],
        'Média de Vagas': [
            df_com_aa['Qnt Vagas Totais'].mean() if len(df_com_aa) > 0 else 0,
            df_sem_aa['Qnt Vagas Totais'].mean() if len(df_sem_aa) > 0 else 0
        ],
        'Total de Vagas': [
            df_com_aa['Qnt Vagas Totais'].sum() if len(df_com_aa) > 0 else 0,
            df_sem_aa['Qnt Vagas Totais'].sum() if len(df_sem_aa) > 0 else 0
        ]
    })
    media_status['Média de Vagas'] = media_status['Média de Vagas'].round(2)
    salvar_tabela(media_status, pasta_vagas, "media_status_aa")
    
    # 6. Média por Região
    if 'Região' in df.columns:
        media_por_regiao = df.groupby('Região').agg({
            'Qnt Vagas Totais': ['mean', 'sum', 'count']
        }).reset_index()
        media_por_regiao.columns = ['Região', 'Média de Vagas', 'Total de Vagas', 'Qtd Programas']
        media_por_regiao['Média de Vagas'] = media_por_regiao['Média de Vagas'].round(2)
        media_por_regiao = media_por_regiao.sort_values('Média de Vagas', ascending=False)
        salvar_tabela(media_por_regiao, pasta_vagas, "media_regiao")
    
    # 7. Média por Tipo de IES
    if 'Tipo de IES' in df.columns:
        media_por_ies = df.groupby('Tipo de IES').agg({
            'Qnt Vagas Totais': ['mean', 'sum', 'count']
        }).reset_index()
        media_por_ies.columns = ['Tipo de IES', 'Média de Vagas', 'Total de Vagas', 'Qtd Programas']
        media_por_ies['Média de Vagas'] = media_por_ies['Média de Vagas'].round(2)
        media_por_ies = media_por_ies.sort_values('Média de Vagas', ascending=False)
        salvar_tabela(media_por_ies, pasta_vagas, "media_tipo_ies")
    
    # 8. Top Programas com mais Vagas AA
    df_top_aa = df[df['Vagas Totais AA'] > 0].nlargest(20, 'Vagas Totais AA')
    
    if len(df_top_aa) > 0:
        # Selecionar apenas colunas que existem
        colunas_desejadas = ['Nome do Programa', 'Sigla da IES', 'UF', 'Região', 
                            'Nota', 'Qnt Vagas Totais', 'Vagas Totais AA', 
                            'Vagas Totais Agregadas', 'Vagas Totais Por Grupo/Exclusivas']
        colunas_existentes = [col for col in colunas_desejadas if col in df_top_aa.columns]
        
        top_programas = df_top_aa[colunas_existentes].copy()
        top_programas['% AA'] = (top_programas['Vagas Totais AA'] / top_programas['Qnt Vagas Totais'] * 100).round(2)
        salvar_tabela(top_programas, pasta_vagas, "top_20_programas_vagas_aa")
    
    # 9. Distribuição por UF
    if 'UF' in df.columns:
        vagas_por_uf = df.groupby('UF').agg({
            'Qnt Vagas Totais': 'sum',
            'Vagas Totais AA': 'sum',
            'Nome do Programa': 'count'
        }).reset_index()
        vagas_por_uf.columns = ['UF', 'Total Vagas', 'Vagas AA', 'Qtd Programas']
        vagas_por_uf['% AA'] = (vagas_por_uf['Vagas AA'] / vagas_por_uf['Total Vagas'] * 100).round(2)
        vagas_por_uf = vagas_por_uf.sort_values('Total Vagas', ascending=False)
        salvar_tabela(vagas_por_uf, pasta_vagas, "distribuicao_uf")
    
    print(f"    [OK] Tabelas de Análise de Vagas salvas em: {pasta_vagas}")

def exportar_tabelas_grupos_sociais(df, area_nome, pasta_destino):
    """Exporta todas as tabelas da página Grupos Sociais"""
    print(f"  Exportando tabelas de Grupos Sociais para {area_nome}...")
    
    pasta_grupos = pasta_destino / "grupos_sociais"
    pasta_grupos.mkdir(exist_ok=True, parents=True)
    
    # 1. Visão Geral dos Grupos
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
                '% Programas': round((programas_com_grupo / len(df) * 100), 2) if len(df) > 0 else 0
            })
    
    df_grupos = pd.DataFrame(grupos_stats).sort_values('Programas', ascending=False)
    salvar_tabela(df_grupos, pasta_grupos, "visao_geral_grupos")
    
    # 2. Múltiplos Grupos por Programa
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
                'IES': row.get('Sigla da IES', 'N/A'),
                'UF': row.get('UF', 'N/A'),
                'Região': row.get('Região', 'N/A'),
                'Quantidade de Grupos': len(grupos_contemplados),
                'Grupos': ', '.join(grupos_contemplados)
            })
    
    if grupos_por_programa:
        df_multiplos = pd.DataFrame(grupos_por_programa).sort_values('Quantidade de Grupos', ascending=False)
        salvar_tabela(df_multiplos, pasta_grupos, "programas_multiplos_grupos")
        
        # Resumo de quantidade de grupos
        resumo_qtd = df_multiplos['Quantidade de Grupos'].value_counts().reset_index()
        resumo_qtd.columns = ['Quantidade de Grupos', 'Quantidade de Programas']
        resumo_qtd = resumo_qtd.sort_values('Quantidade de Grupos')
        salvar_tabela(resumo_qtd, pasta_grupos, "resumo_quantidade_grupos")
    
    # 3. Distribuição Regional por Grupo
    if 'Região' in df.columns:
        regional_data = []
        regioes = sorted(df['Região'].dropna().unique())
        
        for regiao in regioes:
            df_reg = df[df['Região'] == regiao]
            total_reg = len(df_reg)
            
            row_data = {'Região': regiao, 'Total Programas': total_reg}
            
            for nome_grupo, col in GRUPOS_SOCIAIS.items():
                if col in df_reg.columns:
                    qtd = (df_reg[col].fillna('').str.strip().str.upper() == 'SIM').sum()
                    row_data[f'{nome_grupo} (Qtd)'] = qtd
                    row_data[f'{nome_grupo} (%)'] = round((qtd / total_reg * 100), 2) if total_reg > 0 else 0
            
            regional_data.append(row_data)
        
        df_regional = pd.DataFrame(regional_data)
        salvar_tabela(df_regional, pasta_grupos, "distribuicao_regional_grupos")
    
    # 4. Interseccionalidade por Área (apenas para "Todas as Áreas")
    if 'Área' in df.columns and area_nome == "Todas as Áreas":
        data_area = []
        
        for idx, row in df.iterrows():
            count_grupos = 0
            grupos_lista = []
            for nome_grupo, col in GRUPOS_SOCIAIS.items():
                if col in df.columns:
                    if str(row[col]).strip().upper() == 'SIM':
                        count_grupos += 1
                        grupos_lista.append(nome_grupo)
            
            data_area.append({
                'Área': row['Área'],
                'Programa': row.get('Nome do Programa', 'N/A'),
                'Qtd Grupos': count_grupos,
                'Grupos': ', '.join(grupos_lista) if grupos_lista else 'Nenhum'
            })
        
        if data_area:
            df_area_groups = pd.DataFrame(data_area)
            
            # Resumo por área
            area_stats = df_area_groups.groupby('Área').agg({
                'Qtd Grupos': ['mean', 'sum', 'count']
            }).reset_index()
            area_stats.columns = ['Área', 'Média de Grupos por Programa', 'Total de Grupos', 'Qtd Programas']
            area_stats['Média de Grupos por Programa'] = area_stats['Média de Grupos por Programa'].round(2)
            area_stats = area_stats.sort_values('Média de Grupos por Programa', ascending=False)
            salvar_tabela(area_stats, pasta_grupos, "interseccionalidade_area")
            
            # Detalhamento completo
            df_area_groups = df_area_groups.sort_values(['Área', 'Qtd Grupos'], ascending=[True, False])
            salvar_tabela(df_area_groups, pasta_grupos, "detalhamento_grupos_por_area")
    
    # 5. Análise detalhada por grupo
    pasta_por_grupo = pasta_grupos / "por_grupo"
    pasta_por_grupo.mkdir(exist_ok=True, parents=True)
    
    for grupo in df_grupos['Grupo'].tolist():
        coluna_grupo = GRUPOS_SOCIAIS[grupo]
        df_grupo = df[df[coluna_grupo].fillna('').str.strip().str.upper() == 'SIM'].copy()
        
        if len(df_grupo) > 0:
            grupo_normalizado = normalizar_nome_arquivo(grupo)
            
            # Tabela resumo do grupo
            resumo_grupo = {
                'Total de Programas': len(df_grupo),
                'Total de Vagas (Geral)': df_grupo['Qnt Vagas Totais'].sum() if 'Qnt Vagas Totais' in df_grupo.columns else 0
            }
            
            coluna_vagas_grupo = f"Vagas {coluna_grupo.replace('AA ', '')}"
            if coluna_vagas_grupo in df_grupo.columns:
                resumo_grupo['Vagas Específicas do Grupo'] = pd.to_numeric(df_grupo[coluna_vagas_grupo], errors='coerce').fillna(0).sum()
            
            df_resumo = pd.DataFrame([resumo_grupo])
            salvar_tabela(df_resumo, pasta_por_grupo, f"{grupo_normalizado}_resumo")
            
            # Distribuição por Região
            if 'Região' in df_grupo.columns:
                regiao_dist = df_grupo['Região'].value_counts().reset_index()
                regiao_dist.columns = ['Região', 'Quantidade de Programas']
                salvar_tabela(regiao_dist, pasta_por_grupo, f"{grupo_normalizado}_regiao")
            
            # Distribuição por Nota
            if 'Nota' in df_grupo.columns:
                nota_dist = df_grupo['Nota'].value_counts().reset_index()
                nota_dist.columns = ['Nota', 'Quantidade de Programas']
                salvar_tabela(nota_dist, pasta_por_grupo, f"{grupo_normalizado}_nota")
            
            # Distribuição por UF
            if 'UF' in df_grupo.columns:
                uf_dist = df_grupo['UF'].value_counts().reset_index()
                uf_dist.columns = ['UF', 'Quantidade de Programas']
                salvar_tabela(uf_dist, pasta_por_grupo, f"{grupo_normalizado}_uf")
            
            # Lista completa de programas
            colunas_programas_desejadas = ['Nome do Programa', 'Sigla da IES', 'UF', 'Região', 'Nota']
            colunas_programas = [col for col in colunas_programas_desejadas if col in df_grupo.columns]
            
            if coluna_vagas_grupo in df_grupo.columns:
                colunas_programas.append(coluna_vagas_grupo)
            
            programas_grupo = df_grupo[colunas_programas].copy()
            salvar_tabela(programas_grupo, pasta_por_grupo, f"{grupo_normalizado}_programas")
    
    print(f"    [OK] Tabelas de Grupos Sociais salvas em: {pasta_grupos}")

def exportar_tabelas_distribuicao_geografica(df, area_nome, pasta_destino):
    """Exporta todas as tabelas da página Distribuição Geográfica"""
    print(f"  Exportando tabelas de Distribuição Geográfica para {area_nome}...")
    
    pasta_geo = pasta_destino / "distribuicao_geografica"
    pasta_geo.mkdir(exist_ok=True, parents=True)
    
    if 'UF' not in df.columns:
        print(f"    ⚠ Dados geográficos não disponíveis para {area_nome}")
        return
    
    # 1. Distribuição por UF
    uf_stats = df.groupby('UF').agg({
        'Nome do Programa': 'count',
        'Status AA': lambda x: (x == 'Com Editais AA').sum()
    }).reset_index()
    
    uf_stats.columns = ['UF', 'Total Programas', 'Com AA']
    uf_stats['Sem AA'] = uf_stats['Total Programas'] - uf_stats['Com AA']
    uf_stats['% Com AA'] = (uf_stats['Com AA'] / uf_stats['Total Programas'] * 100).round(2)
    
    # Adicionar região
    if 'Região' in df.columns:
        uf_regiao = df[['UF', 'Região']].dropna().drop_duplicates(subset=['UF']).set_index('UF')
        uf_stats['Região'] = uf_stats['UF'].map(uf_regiao['Região'])
        uf_stats = uf_stats[['UF', 'Região', 'Total Programas', 'Com AA', 'Sem AA', '% Com AA']]
    
    uf_stats = uf_stats.sort_values('Total Programas', ascending=False)
    salvar_tabela(uf_stats, pasta_geo, "distribuicao_uf")
    
    # 2. Análise Regional
    if 'Região' in df.columns:
        regiao_stats = df.groupby(['Região', 'Status AA']).size().unstack(fill_value=0).reset_index()
        
        if 'Com Editais AA' in regiao_stats.columns and 'Sem Editais AA' in regiao_stats.columns:
            regiao_stats['Total'] = regiao_stats['Com Editais AA'] + regiao_stats['Sem Editais AA']
            regiao_stats['% Com AA'] = (regiao_stats['Com Editais AA'] / regiao_stats['Total'] * 100).round(2)
            regiao_stats = regiao_stats.sort_values('Total', ascending=False)
            salvar_tabela(regiao_stats, pasta_geo, "analise_regional")
        
        # Distribuição total por região
        total_por_regiao = df['Região'].value_counts().reset_index()
        total_por_regiao.columns = ['Região', 'Quantidade de Programas']
        total_por_regiao['Percentual'] = (total_por_regiao['Quantidade de Programas'] / total_por_regiao['Quantidade de Programas'].sum() * 100).round(2)
        salvar_tabela(total_por_regiao, pasta_geo, "total_por_regiao")
    
    # 3. Heatmap: Geografia x Grupos Sociais
    if 'Região' in df.columns:
        heatmap_data = []
        regioes_unicas = sorted(df['Região'].dropna().unique())
        
        for regiao in regioes_unicas:
            df_reg = df[df['Região'] == regiao]
            total_progs_reg = len(df_reg)
            
            if total_progs_reg > 0:
                row_data = {'Região': regiao, 'Total Programas': total_progs_reg}
                for nome_grupo, col_db in GRUPOS_SOCIAIS.items():
                    if col_db in df_reg.columns:
                        qtd = (df_reg[col_db].fillna('').str.strip().str.upper() == 'SIM').sum()
                        perc = (qtd / total_progs_reg) * 100
                        row_data[f'{nome_grupo} (Qtd)'] = qtd
                        row_data[f'{nome_grupo} (%)'] = round(perc, 2)
                heatmap_data.append(row_data)
        
        if heatmap_data:
            df_heatmap = pd.DataFrame(heatmap_data)
            salvar_tabela(df_heatmap, pasta_geo, "grupos_por_regiao")
    
    # 4. Hierarquia: Região > UF > IES
    if 'Sigla da IES' in df.columns and 'Região' in df.columns:
        hierarquia = df.groupby(['Região', 'UF', 'Sigla da IES']).size().reset_index(name='Quantidade de Programas')
        hierarquia = hierarquia.sort_values(['Região', 'UF', 'Quantidade de Programas'], ascending=[True, True, False])
        salvar_tabela(hierarquia, pasta_geo, "hierarquia_regiao_uf_ies")
        
        # Resumo por IES
        resumo_ies = df.groupby('Sigla da IES').agg({
            'Nome do Programa': 'count',
            'UF': 'first',
            'Região': 'first',
            'Status AA': lambda x: (x == 'Com Editais AA').sum()
        }).reset_index()
        resumo_ies.columns = ['IES', 'Total Programas', 'UF', 'Região', 'Com AA']
        resumo_ies['% Com AA'] = (resumo_ies['Com AA'] / resumo_ies['Total Programas'] * 100).round(2)
        resumo_ies = resumo_ies.sort_values('Total Programas', ascending=False)
        salvar_tabela(resumo_ies, pasta_geo, "resumo_por_ies")
    
    # 5. Programas por Estado (detalhado)
    colunas_base = ['Nome do Programa', 'Sigla da IES', 'UF', 'Região', 
                    'Nota', 'Status AA', 'Tipo de IES']
    colunas_detalhado = [col for col in colunas_base if col in df.columns]
    
    programas_detalhado = df[colunas_detalhado].copy()
    
    if 'Qnt Vagas Totais' in df.columns:
        programas_detalhado['Vagas Totais'] = df['Qnt Vagas Totais']
    if 'Vagas Totais AA' in df.columns:
        programas_detalhado['Vagas AA'] = df['Vagas Totais AA']
    
    # Ordenar por colunas disponíveis
    colunas_ordenacao = [col for col in ['Região', 'UF', 'Nome do Programa'] if col in programas_detalhado.columns]
    if colunas_ordenacao:
        programas_detalhado = programas_detalhado.sort_values(colunas_ordenacao)
    
    salvar_tabela(programas_detalhado, pasta_geo, "programas_detalhado")
    
    print(f"    [OK] Tabelas de Distribuição Geográfica salvas em: {pasta_geo}")

def main():
    """Função principal"""
    print("=" * 80)
    print("EXPORTAÇÃO DE TABELAS - ANÁLISE DE VAGAS E GRUPOS SOCIAIS")
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
            print(f"  [SKIP] Pulando planilha '{sheet_name}' - colunas necessárias não encontradas")
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
    
    print(f"[OK] Dados carregados: {len(areas_data)} áreas encontradas")
    print()
    
    # Criar pasta base
    pasta_base = criar_estrutura_pastas("tabelas_exportadas")
    print(f"[OK] Pasta base criada: {pasta_base.absolute()}")
    print()
    
    # Processar "Todas as Áreas"
    print("Processando: Todas as Áreas")
    pasta_todas = pasta_base / "Todas_as_Areas"
    pasta_todas.mkdir(exist_ok=True, parents=True)
    
    exportar_tabelas_analise_vagas(df_todas_areas.copy(), "Todas as Áreas", pasta_todas)
    exportar_tabelas_grupos_sociais(df_todas_areas.copy(), "Todas as Áreas", pasta_todas)
    exportar_tabelas_distribuicao_geografica(df_todas_areas.copy(), "Todas as Áreas", pasta_todas)
    print()
    
    # Processar cada área individual
    for area_nome, df_area in areas_data.items():
        print(f"Processando: {area_nome}")
        pasta_area = pasta_base / normalizar_nome_arquivo(area_nome)
        pasta_area.mkdir(exist_ok=True, parents=True)
        
        exportar_tabelas_analise_vagas(df_area.copy(), area_nome, pasta_area)
        exportar_tabelas_grupos_sociais(df_area.copy(), area_nome, pasta_area)
        exportar_tabelas_distribuicao_geografica(df_area.copy(), area_nome, pasta_area)
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
    print(f"  └── tabelas_exportadas/")
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
    print("Formatos: Cada tabela foi salva em .csv e .xlsx")
    print()

if __name__ == "__main__":
    main()

"""
Script para exportar todas as tabelas em um único arquivo PDF organizado por áreas.
Cada área terá suas próprias seções no PDF.
"""
import os
import pandas as pd
from pathlib import Path
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, PageBreak, Spacer
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from config import GRUPOS_SOCIAIS, ORDEM_NOTAS

def normalizar_nome_arquivo(nome):
    """Normaliza nome para usar em arquivo"""
    return nome.replace(' ', '_').replace('/', '_').replace('\\', '_').lower()

def criar_tabela_pdf(df, titulo, styles):
    """Cria uma tabela formatada para o PDF"""
    elementos = []
    
    # Adicionar título
    elementos.append(Paragraph(titulo, styles['CustomHeading2']))
    elementos.append(Spacer(1, 12))
    
    if df.empty:
        elementos.append(Paragraph("Sem dados disponíveis", styles['Normal']))
        elementos.append(Spacer(1, 12))
        return elementos
    
    # Limitar número de linhas se muito grande
    max_rows = 50
    if len(df) > max_rows:
        df_display = df.head(max_rows)
        nota_truncamento = True
    else:
        df_display = df
        nota_truncamento = False
    
    # Preparar dados para a tabela
    data = [df_display.columns.tolist()] + df_display.values.tolist()
    
    # Criar tabela
    try:
        # Ajustar largura das colunas
        num_cols = len(df_display.columns)
        col_width = 7.5 * inch / num_cols  # Distribuir largura disponível
        
        table = Table(data, colWidths=[col_width] * num_cols)
        
        # Estilo da tabela
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 7),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        
        elementos.append(table)
        
        if nota_truncamento:
            elementos.append(Spacer(1, 6))
            elementos.append(Paragraph(f"<i>Mostrando {max_rows} de {len(df)} linhas</i>", styles['Normal']))
        
    except Exception as e:
        elementos.append(Paragraph(f"Erro ao criar tabela: {str(e)}", styles['Normal']))
    
    elementos.append(Spacer(1, 20))
    return elementos

def gerar_tabelas_analise_vagas(df, area_nome, styles):
    """Gera tabelas da seção Análise de Vagas"""
    elementos = []
    
    # Título da seção
    elementos.append(Paragraph(f"ANÁLISE DE VAGAS - {area_nome}", styles['CustomHeading1']))
    elementos.append(Spacer(1, 12))
    
    # Converter colunas de vagas para numérico
    for col in ['Qnt Vagas Totais', 'Vagas Totais AA', 'Vagas Totais Agregadas', 'Vagas Totais Por Grupo/Exclusivas']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    # 1. Resumo Geral
    total_vagas_gerais = df['Qnt Vagas Totais'].sum()
    total_vagas_aa = df['Vagas Totais AA'].sum()
    total_vagas_agregadas = df['Vagas Totais Agregadas'].sum()
    total_vagas_por_grupo = df['Vagas Totais Por Grupo/Exclusivas'].sum()
    
    resumo_geral = pd.DataFrame({
        'Categoria': ['Vagas Totais', 'Vagas AA (Total)', 'Vagas Agregadas', 'Vagas Por Grupo'],
        'Quantidade': [total_vagas_gerais, total_vagas_aa, total_vagas_agregadas, total_vagas_por_grupo],
        'Percentual': [
            100.0,
            (total_vagas_aa / total_vagas_gerais * 100) if total_vagas_gerais > 0 else 0,
            (total_vagas_agregadas / total_vagas_gerais * 100) if total_vagas_gerais > 0 else 0,
            (total_vagas_por_grupo / total_vagas_gerais * 100) if total_vagas_gerais > 0 else 0
        ]
    })
    resumo_geral['Percentual'] = resumo_geral['Percentual'].round(2).astype(str) + '%'
    elementos.extend(criar_tabela_pdf(resumo_geral, "Resumo Geral de Vagas", styles))
    
    # 2. Distribuição por Região
    if 'Região' in df.columns:
        vagas_por_regiao = df.groupby('Região').agg({
            'Qnt Vagas Totais': 'sum',
            'Vagas Totais AA': 'sum',
            'Nome do Programa': 'count'
        }).reset_index()
        vagas_por_regiao.columns = ['Região', 'Total Vagas', 'Vagas AA', 'Qtd Programas']
        vagas_por_regiao['% AA'] = (vagas_por_regiao['Vagas AA'] / vagas_por_regiao['Total Vagas'] * 100).round(2)
        vagas_por_regiao = vagas_por_regiao.sort_values('Total Vagas', ascending=False)
        elementos.extend(criar_tabela_pdf(vagas_por_regiao, "Distribuição por Região", styles))
    
    # 3. Distribuição por Nota CAPES
    if 'Nota' in df.columns:
        vagas_por_nota = df.groupby('Nota').agg({
            'Qnt Vagas Totais': 'sum',
            'Vagas Totais AA': 'sum',
            'Nome do Programa': 'count'
        }).reset_index()
        vagas_por_nota.columns = ['Nota', 'Total Vagas', 'Vagas AA', 'Qtd Programas']
        vagas_por_nota['% AA'] = (vagas_por_nota['Vagas AA'] / vagas_por_nota['Total Vagas'] * 100).round(2)
        elementos.extend(criar_tabela_pdf(vagas_por_nota, "Distribuição por Nota CAPES", styles))
    
    # 4. Top 10 Programas
    df_top_aa = df[df['Vagas Totais AA'] > 0].nlargest(10, 'Vagas Totais AA')
    if len(df_top_aa) > 0:
        colunas_desejadas = ['Nome do Programa', 'Sigla da IES', 'UF', 'Vagas Totais AA']
        colunas_existentes = [col for col in colunas_desejadas if col in df_top_aa.columns]
        top_programas = df_top_aa[colunas_existentes].copy()
        elementos.extend(criar_tabela_pdf(top_programas, "Top 10 Programas - Mais Vagas AA", styles))
    
    return elementos

def gerar_tabelas_grupos_sociais(df, area_nome, styles):
    """Gera tabelas da seção Grupos Sociais"""
    elementos = []
    
    # Título da seção
    elementos.append(PageBreak())
    elementos.append(Paragraph(f"GRUPOS SOCIAIS - {area_nome}", styles['CustomHeading1']))
    elementos.append(Spacer(1, 12))
    
    # 1. Visão Geral dos Grupos
    grupos_stats = []
    for nome_grupo, coluna in GRUPOS_SOCIAIS.items():
        if coluna in df.columns:
            programas_com_grupo = (df[coluna].fillna('').str.strip().str.upper() == 'SIM').sum()
            grupos_stats.append({
                'Grupo': nome_grupo,
                'Programas': int(programas_com_grupo),
                '% Programas': round((programas_com_grupo / len(df) * 100), 2) if len(df) > 0 else 0
            })
    
    df_grupos = pd.DataFrame(grupos_stats).sort_values('Programas', ascending=False)
    elementos.extend(criar_tabela_pdf(df_grupos, "Visão Geral dos Grupos", styles))
    
    # 2. Distribuição Regional por Grupo (resumo)
    if 'Região' in df.columns and len(df_grupos) > 0:
        regional_data = []
        regioes = sorted(df['Região'].dropna().unique())
        
        for regiao in regioes[:5]:  # Limitar a 5 regiões para caber no PDF
            df_reg = df[df['Região'] == regiao]
            total_reg = len(df_reg)
            
            row_data = {'Região': regiao, 'Total': total_reg}
            
            # Pegar apenas os 5 grupos principais
            for grupo in df_grupos['Grupo'].head(5):
                col = GRUPOS_SOCIAIS[grupo]
                if col in df_reg.columns:
                    qtd = (df_reg[col].fillna('').str.strip().str.upper() == 'SIM').sum()
                    row_data[grupo[:15]] = f"{qtd} ({round((qtd/total_reg*100), 1)}%)" if total_reg > 0 else "0"
            
            regional_data.append(row_data)
        
        if regional_data:
            df_regional = pd.DataFrame(regional_data)
            elementos.extend(criar_tabela_pdf(df_regional, "Distribuição Regional (Top 5 Grupos)", styles))
    
    return elementos

def gerar_tabelas_distribuicao_geografica(df, area_nome, styles):
    """Gera tabelas da seção Distribuição Geográfica"""
    elementos = []
    
    # Título da seção
    elementos.append(PageBreak())
    elementos.append(Paragraph(f"DISTRIBUIÇÃO GEOGRÁFICA - {area_nome}", styles['CustomHeading1']))
    elementos.append(Spacer(1, 12))
    
    if 'UF' not in df.columns:
        elementos.append(Paragraph("Dados geográficos não disponíveis", styles['Normal']))
        return elementos
    
    # 1. Distribuição por UF (Top 15)
    uf_stats = df.groupby('UF').agg({
        'Nome do Programa': 'count',
        'Status AA': lambda x: (x == 'Com Editais AA').sum()
    }).reset_index()
    uf_stats.columns = ['UF', 'Total', 'Com AA']
    uf_stats['% AA'] = (uf_stats['Com AA'] / uf_stats['Total'] * 100).round(2)
    uf_stats = uf_stats.sort_values('Total', ascending=False).head(15)
    elementos.extend(criar_tabela_pdf(uf_stats, "Top 15 Estados - Quantidade de Programas", styles))
    
    # 2. Análise Regional
    if 'Região' in df.columns:
        regiao_stats = df.groupby('Região').agg({
            'Nome do Programa': 'count',
            'Status AA': lambda x: (x == 'Com Editais AA').sum()
        }).reset_index()
        regiao_stats.columns = ['Região', 'Total', 'Com AA']
        regiao_stats['Sem AA'] = regiao_stats['Total'] - regiao_stats['Com AA']
        regiao_stats['% AA'] = (regiao_stats['Com AA'] / regiao_stats['Total'] * 100).round(2)
        regiao_stats = regiao_stats.sort_values('Total', ascending=False)
        elementos.extend(criar_tabela_pdf(regiao_stats, "Análise Regional", styles))
    
    return elementos

def main():
    """Função principal"""
    print("=" * 80)
    print("EXPORTAÇÃO DE TABELAS EM PDF - ANÁLISE DE VAGAS E GRUPOS SOCIAIS")
    print("=" * 80)
    print()
    
    # Carregar dados
    print("Carregando dados...")
    excel_file = pd.ExcelFile('dados_brutos.xlsx')
    areas_data = {}
    
    for sheet_name in excel_file.sheet_names:
        df_area = pd.read_excel(excel_file, sheet_name=sheet_name)
        
        if 'Editais AA' not in df_area.columns or 'Nome do Programa' not in df_area.columns:
            print(f"  [SKIP] Pulando planilha '{sheet_name}' - colunas necessárias não encontradas")
            continue
        
        df_area['Área'] = sheet_name
        if 'Nota' in df_area.columns:
            df_area['Nota'] = df_area['Nota'].astype(str).str.strip()
        df_area['Status AA'] = df_area['Editais AA'].apply(
            lambda x: 'Com Editais AA' if str(x).upper() == 'SIM' else 'Sem Editais AA'
        )
        areas_data[sheet_name] = df_area
    
    df_todas_areas = pd.concat(areas_data.values(), ignore_index=True)
    
    print(f"[OK] Dados carregados: {len(areas_data)} áreas encontradas")
    print()
    
    # Criar PDF
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    pdf_filename = f"relatorio_tabelas_{timestamp}.pdf"
    
    print(f"Criando PDF: {pdf_filename}")
    
    # Configurar documento PDF em paisagem para mais espaço
    doc = SimpleDocTemplate(
        pdf_filename,
        pagesize=landscape(A4),
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=18,
    )
    
    # Estilos
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name='CustomHeading1',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#1f4788'),
        spaceAfter=12,
        spaceBefore=12
    ))
    styles.add(ParagraphStyle(
        name='CustomHeading2',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=colors.HexColor('#2e5c8a'),
        spaceAfter=6,
        spaceBefore=6
    ))
    
    # Elementos do PDF
    elementos = []
    
    # Página de título
    titulo_style = ParagraphStyle(
        name='Titulo',
        fontSize=24,
        textColor=colors.HexColor('#1f4788'),
        alignment=1,  # Centro
        spaceAfter=20
    )
    elementos.append(Spacer(1, 2*inch))
    elementos.append(Paragraph("RELATÓRIO DE ANÁLISE", titulo_style))
    elementos.append(Paragraph("Ações Afirmativas em Programas de Pós-Graduação", styles['Heading2']))
    elementos.append(Spacer(1, 0.5*inch))
    elementos.append(Paragraph(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
    elementos.append(Paragraph(f"Total de Áreas: {len(areas_data) + 1} (incluindo 'Todas as Áreas')", styles['Normal']))
    elementos.append(PageBreak())
    
    # Processar "Todas as Áreas"
    print("  Processando: Todas as Áreas")
    elementos.extend(gerar_tabelas_analise_vagas(df_todas_areas.copy(), "Todas as Áreas", styles))
    elementos.extend(gerar_tabelas_grupos_sociais(df_todas_areas.copy(), "Todas as Áreas", styles))
    elementos.extend(gerar_tabelas_distribuicao_geografica(df_todas_areas.copy(), "Todas as Áreas", styles))
    
    # Processar cada área individual
    for i, (area_nome, df_area) in enumerate(areas_data.items(), 1):
        print(f"  Processando: {area_nome} ({i}/{len(areas_data)})")
        elementos.append(PageBreak())
        elementos.extend(gerar_tabelas_analise_vagas(df_area.copy(), area_nome, styles))
        elementos.extend(gerar_tabelas_grupos_sociais(df_area.copy(), area_nome, styles))
        elementos.extend(gerar_tabelas_distribuicao_geografica(df_area.copy(), area_nome, styles))
    
    # Gerar PDF
    print("\nGerando arquivo PDF...")
    try:
        doc.build(elementos)
        print()
        print("=" * 80)
        print("EXPORTAÇÃO CONCLUÍDA COM SUCESSO!")
        print("=" * 80)
        print()
        print(f"📄 Arquivo PDF criado: {pdf_filename}")
        print(f"📊 Áreas incluídas: {len(areas_data) + 1} (incluindo 'Todas as Áreas')")
        print()
        print("O PDF contém:")
        print("  ✓ Página de título")
        print("  ✓ Análise de Vagas (resumo, distribuição regional, por nota, top programas)")
        print("  ✓ Grupos Sociais (visão geral, distribuição regional)")
        print("  ✓ Distribuição Geográfica (por UF, análise regional)")
        print()
    except Exception as e:
        print(f"\n❌ Erro ao gerar PDF: {str(e)}")
        print("Verifique se a biblioteca reportlab está instalada: pip install reportlab")

if __name__ == "__main__":
    main()

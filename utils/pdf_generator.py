"""
Gerador de Relatórios em PDF para o Dashboard de Ações Afirmativas
Utiliza ReportLab para criar relatórios profissionais
"""
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.platypus.flowables import HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from datetime import datetime
from io import BytesIO
import pandas as pd


def criar_estilos():
    """Cria estilos personalizados para o PDF"""
    styles = getSampleStyleSheet()
    
    # Estilo para título principal
    styles.add(ParagraphStyle(
        name='CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2C3E50'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    ))
    
    # Estilo para subtítulos
    styles.add(ParagraphStyle(
        name='CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#34495E'),
        spaceAfter=12,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    ))
    
    # Estilo para texto normal
    styles.add(ParagraphStyle(
        name='CustomBody',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#2C3E50'),
        alignment=TA_JUSTIFY
    ))
    
    return styles


def criar_cabecalho(area_selecionada):
    """Cria cabeçalho do relatório"""
    styles = criar_estilos()
    story = []
    
    # Título
    story.append(Paragraph("Dashboard de Ações Afirmativas - CAPES", styles['CustomTitle']))
    story.append(Paragraph(f"<b>Colégio de Humanidades</b>", styles['CustomBody']))
    story.append(Spacer(1, 12))
    
    # Informações do relatório
    data_geracao = datetime.now().strftime('%d/%m/%Y %H:%M')
    story.append(Paragraph(f"<b>Área:</b> {area_selecionada}", styles['CustomBody']))
    story.append(Paragraph(f"<b>Data de Geração:</b> {data_geracao}", styles['CustomBody']))
    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#3498DB')))
    story.append(Spacer(1, 20))
    
    return story


def criar_tabela_estatisticas(stats):
    """Cria tabela com estatísticas gerais"""
    data = [
        ['Estatística', 'Valor'],
        ['Total de Programas', str(stats['total_programas'])],
        ['Programas com Editais AA', f"{stats['com_aa']} ({stats['percentual_aa']:.1f}%)"],
        ['Programas sem Editais AA', f"{stats['sem_aa']} ({100-stats['percentual_aa']:.1f}%)"],
        ['Total de Vagas', f"{stats['total_vagas']:,}"],
        ['Vagas AA', f"{stats['total_vagas_aa']:,}"],
        ['Regiões Únicas', str(stats['regioes_unicas'])],
        ['UFs Únicas', str(stats['ufs_unicas'])],
    ]
    
    table = Table(data, colWidths=[3*inch, 2*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498DB')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#ECF0F1')]),
    ]))
    
    return table


def criar_tabela_distribuicao(df, coluna, titulo):
    """Cria tabela de distribuição para uma coluna específica"""
    if coluna not in df.columns:
        return None
    
    distribuicao = df[coluna].value_counts().reset_index()
    distribuicao.columns = [coluna, 'Quantidade']
    distribuicao['Percentual'] = (distribuicao['Quantidade'] / distribuicao['Quantidade'].sum() * 100).round(1)
    distribuicao['Percentual'] = distribuicao['Percentual'].astype(str) + '%'
    
    # Limitar a 15 linhas
    if len(distribuicao) > 15:
        outros = pd.DataFrame({
            coluna: ['Outros'],
            'Quantidade': [distribuicao.iloc[15:]['Quantidade'].sum()],
            'Percentual': [f"{distribuicao.iloc[15:]['Quantidade'].sum() / df.shape[0] * 100:.1f}%"]
        })
        distribuicao = pd.concat([distribuicao.head(15), outros], ignore_index=True)
    
    # Criar tabela
    data = [distribuicao.columns.tolist()] + distribuicao.values.tolist()
    
    table = Table(data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2ECC71')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#ECF0F1')]),
    ]))
    
    return table


def gerar_pdf_resumo(df, area_selecionada, stats):
    """
    Gera relatório resumo executivo em PDF
    
    Args:
        df: DataFrame com dados
        area_selecionada: nome da área
        stats: dicionário com estatísticas
        
    Returns:
        BytesIO com PDF gerado
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    
    story = []
    styles = criar_estilos()
    
    # Cabeçalho
    story.extend(criar_cabecalho(area_selecionada))
    
    # Seção: Resumo Executivo
    story.append(Paragraph("Resumo Executivo", styles['CustomHeading']))
    story.append(Spacer(1, 12))
    
    # Estatísticas gerais
    story.append(criar_tabela_estatisticas(stats))
    story.append(Spacer(1, 20))
    
    # Distribuição por Região
    if 'Região' in df.columns:
        story.append(Paragraph("Distribuição por Região", styles['CustomHeading']))
        story.append(Spacer(1, 12))
        tabela_regiao = criar_tabela_distribuicao(df, 'Região', 'Região')
        if tabela_regiao:
            story.append(tabela_regiao)
        story.append(Spacer(1, 20))
    
    # Distribuição por Nota
    if 'NOTA' in df.columns:
        story.append(Paragraph("Distribuição por Nota CAPES", styles['CustomHeading']))
        story.append(Spacer(1, 12))
        tabela_nota = criar_tabela_distribuicao(df, 'NOTA', 'Nota')
        if tabela_nota:
            story.append(tabela_nota)
        story.append(Spacer(1, 20))
    
    # Rodapé
    story.append(Spacer(1, 30))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.grey))
    story.append(Spacer(1, 12))
    rodape = Paragraph(
        f"<i>Dashboard de Ações Afirmativas - CAPES | Gerado em {datetime.now().strftime('%d/%m/%Y %H:%M')}</i>",
        styles['CustomBody']
    )
    story.append(rodape)
    
    # Construir PDF
    doc.build(story)
    buffer.seek(0)
    return buffer


def gerar_pdf_grupos_sociais(df, grupos_data, area_selecionada):
    """
    Gera relatório focado em grupos sociais em PDF
    
    Args:
        df: DataFrame com dados
        grupos_data: DataFrame com estatísticas de grupos
        area_selecionada: nome da área
        
    Returns:
        BytesIO com PDF gerado
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    
    story = []
    styles = criar_estilos()
    
    # Cabeçalho
    story.extend(criar_cabecalho(area_selecionada))
    
    # Título da seção
    story.append(Paragraph("Análise por Grupos Sociais", styles['CustomHeading']))
    story.append(Spacer(1, 12))
    
    # Introdução
    intro_text = f"""
    Este relatório apresenta a análise detalhada das ações afirmativas por grupo social 
    contemplado nos programas de pós-graduação. Total de programas analisados: <b>{len(df)}</b>.
    """
    story.append(Paragraph(intro_text, styles['CustomBody']))
    story.append(Spacer(1, 20))
    
    # Tabela de grupos
    if len(grupos_data) > 0:
        data = [['Grupo Social', 'Programas', '% do Total', 'Vagas']]
        for _, row in grupos_data.iterrows():
            data.append([
                row['Grupo'],
                str(row['Programas']),
                f"{row['% Programas']}%",
                str(int(row.get('Vagas', 0)))
            ])
        
        table = Table(data, colWidths=[2.5*inch, 1.2*inch, 1.2*inch, 1.2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#9B59B6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#ECF0F1')]),
        ]))
        
        story.append(table)
    
    # Rodapé
    story.append(Spacer(1, 30))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.grey))
    story.append(Spacer(1, 12))
    rodape = Paragraph(
        f"<i>Dashboard de Ações Afirmativas - CAPES | Gerado em {datetime.now().strftime('%d/%m/%Y %H:%M')}</i>",
        styles['CustomBody']
    )
    story.append(rodape)
    
    # Construir PDF
    doc.build(story)
    buffer.seek(0)
    return buffer


def gerar_pdf_comparacao(programas_df, area_selecionada):
    """
    Gera PDF com comparação de programas
    
    Args:
        programas_df: DataFrame com programas selecionados para comparação
        area_selecionada: nome da área
        
    Returns:
        BytesIO com PDF gerado
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    
    story = []
    styles = criar_estilos()
    
    # Cabeçalho
    story.extend(criar_cabecalho(area_selecionada))
    
    # Título
    story.append(Paragraph(f"Comparação de Programas ({len(programas_df)} programas)", styles['CustomHeading']))
    story.append(Spacer(1, 12))
    
    # Tabela comparativa
    colunas_comparacao = ['Nome do Programa', 'Sigla da IES', 'UF', 'Região', 'NOTA', 
                         'Tipo de IES', 'Modalidade de Ensino', 'Status AA']
    colunas_disponiveis = [col for col in colunas_comparacao if col in programas_df.columns]
    
    # Transpor para comparação lado a lado
    df_transposto = programas_df[colunas_disponiveis].T
    df_transposto.columns = [f'Programa {i+1}' for i in range(len(programas_df))]
    
    # Criar tabela
    data = [['Característica'] + df_transposto.columns.tolist()]
    for idx, row in df_transposto.iterrows():
        data.append([idx] + row.tolist())
    
    # Ajustar larguras das colunas dinamicamente
    num_programas = len(programas_df)
    largura_caracteristica = 2*inch
    largura_programa = (6*inch) / num_programas
    col_widths = [largura_caracteristica] + [largura_programa] * num_programas
    
    table = Table(data, colWidths=col_widths)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E74C3C')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#ECF0F1')]),
        ('BACKGROUND', (0, 1), (0, -1), colors.HexColor('#BDC3C7')),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
    ]))
    
    story.append(table)
    
    # Rodapé
    story.append(Spacer(1, 30))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.grey))
    story.append(Spacer(1, 12))
    rodape = Paragraph(
        f"<i>Dashboard de Ações Afirmativas - CAPES | Gerado em {datetime.now().strftime('%d/%m/%Y %H:%M')}</i>",
        styles['CustomBody']
    )
    story.append(rodape)
    
    # Construir PDF
    doc.build(story)
    buffer.seek(0)
    return buffer

"""
📥 Exportar Dados - Relatórios e Downloads
Geração de relatórios e exportação de dados em diversos formatos
"""
import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO
from utils.data_loader import load_all_areas, get_data_for_area, prepare_dataframe, get_summary_stats
from utils.filters import render_area_selector, render_global_filters

# Configuração da página
st.set_page_config(
    page_title="Exportar Dados | Dashboard AA",
    page_icon="📥",
    layout="wide"
)

# Carregar dados
areas_data, df_todas_areas, lista_areas = load_all_areas()

# Sidebar
st.sidebar.markdown("# 📥 Exportar Dados")
st.sidebar.markdown("Gere relatórios e exporte dados")
st.sidebar.markdown("---")

# Seletor de Área
area_selecionada = render_area_selector(lista_areas)

# Obter dados
df = get_data_for_area(area_selecionada, areas_data, df_todas_areas)
df = prepare_dataframe(df)

# Filtros
df_filtrado, filtros_ativos = render_global_filters(df)

# ==================== FUNÇÕES DE EXPORTAÇÃO ====================

def to_excel(df, sheet_name='Dados'):
    """Converte DataFrame para Excel em bytes"""
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name=sheet_name, index=False)
    return output.getvalue()

def gerar_relatorio_resumo(df):
    """Gera relatório resumo em texto"""
    stats = get_summary_stats(df)
    
    relatorio = f"""
RELATÓRIO RESUMO - DASHBOARD DE AÇÕES AFIRMATIVAS
Data de Geração: {datetime.now().strftime('%d/%m/%Y %H:%M')}
Área Selecionada: {area_selecionada}
Filtros Ativos: {filtros_ativos}

==================== ESTATÍSTICAS GERAIS ====================

Total de Programas: {stats['total_programas']}
Programas com Editais AA: {stats['com_aa']} ({stats['percentual_aa']:.1f}%)
Programas sem Editais AA: {stats['sem_aa']} ({100-stats['percentual_aa']:.1f}%)

Total de Vagas: {stats['total_vagas']:,}
Vagas AA: {stats['total_vagas_aa']:,}

Áreas Únicas: {stats['areas_unicas']}
Regiões Únicas: {stats['regioes_unicas']}
UFs Únicas: {stats['ufs_unicas']}

==================== DISTRIBUIÇÃO POR REGIÃO ====================
"""
    
    if 'Região' in df.columns:
        regiao_dist = df['Região'].value_counts()
        for regiao, count in regiao_dist.items():
            relatorio += f"\n{regiao}: {count} programas"
    
    relatorio += "\n\n==================== DISTRIBUIÇÃO POR NOTA ====================\n"
    
    if 'NOTA' in df.columns:
        nota_dist = df['NOTA'].value_counts().sort_index()
        for nota, count in nota_dist.items():
            relatorio += f"\nNota {nota}: {count} programas"
    
    return relatorio

# ==================== CONTEÚDO ====================

st.title("📥 Exportar Dados e Relatórios")
st.markdown("Exporte os dados filtrados em diversos formatos")
st.markdown("---")

# Informações sobre os dados atuais
col_info1, col_info2, col_info3 = st.columns(3)

with col_info1:
    st.info(f"""
    **Área Selecionada**  
    {area_selecionada}
    """)

with col_info2:
    st.info(f"""
    **Filtros Ativos**  
    {filtros_ativos} filtro(s)
    """)

with col_info3:
    st.info(f"""
    **Registros**  
    {len(df_filtrado)} programa(s)
    """)

st.markdown("---")

# Seção de Exportação
st.markdown("## 📊 Dados Completos")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📄 Formato CSV")
    st.markdown("""
    - Compatível com Excel, Google Sheets
    - Tamanho pequeno
    - Formato universal
    """)
    
    # CSV com dados filtrados
    csv_data = df_filtrado.to_csv(index=False, encoding='utf-8-sig')
    st.download_button(
        label="📥 Download CSV - Dados Filtrados",
        data=csv_data,
        file_name=f"dados_aa_{area_selecionada.replace(' ', '_').lower()}_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        mime="text/csv",
        use_container_width=True
    )

with col2:
    st.markdown("### 📗 Formato Excel")
    st.markdown("""
    - Formato nativo do Excel
    - Preserva formatação
    - Melhor para análises
    """)
    
    # Excel com dados filtrados
    excel_data = to_excel(df_filtrado, sheet_name='Dados AA')
    st.download_button(
        label="📥 Download Excel - Dados Filtrados",
        data=excel_data,
        file_name=f"dados_aa_{area_selecionada.replace(' ', '_').lower()}_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

st.markdown("---")

# Relatórios em PDF
st.markdown("## 📄 Relatórios em PDF")
st.markdown("Relatórios formatados prontos para impressão ou compartilhamento")

from utils.pdf_generator import gerar_pdf_resumo, gerar_pdf_grupos_sociais

col_pdf1, col_pdf2 = st.columns(2)

with col_pdf1:
    st.markdown("### 📝 Relatório Executivo")
    st.markdown("Resumo com principais estatísticas e gráficos de distribuição.")
    
    if st.button("📄 Gerar PDF Resumo", use_container_width=True):
        with st.spinner("Gerando PDF..."):
            try:
                stats = get_summary_stats(df_filtrado)
                pdf_resumo = gerar_pdf_resumo(df_filtrado, area_selecionada, stats)
                
                st.download_button(
                    label="📥 Baixar PDF Resumo",
                    data=pdf_resumo,
                    file_name=f"relatorio_resumo_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                    key='btn_pdf_resumo_download'
                )
                st.success("PDF gerado com sucesso!")
            except Exception as e:
                st.error(f"Erro ao gerar PDF: {str(e)}")

with col_pdf2:
    st.markdown("### 👥 Relatório de Grupos")
    st.markdown("Análise focada nos grupos sociais contemplados.")
    
    if st.button("📄 Gerar PDF Grupos", use_container_width=True):
        with st.spinner("Gerando PDF..."):
            try:
                # Preparar dados de grupos
                from config import GRUPOS_SOCIAIS
                grupos_data = []
                for nome_grupo, coluna in GRUPOS_SOCIAIS.items():
                    if coluna in df_filtrado.columns:
                        count = (df_filtrado[coluna].fillna('').str.strip().str.upper() == 'SIM').sum()
                        # Tentar pegar vagas
                        col_vagas = f"Vagas {coluna.replace('AA ', '')}"
                        vagas = 0
                        if col_vagas in df_filtrado.columns:
                            vagas = pd.to_numeric(df_filtrado[col_vagas], errors='coerce').fillna(0).sum()
                            
                        grupos_data.append({
                            'Grupo': nome_grupo,
                            'Programas': count,
                            '% Programas': round((count / len(df_filtrado) * 100), 1) if len(df_filtrado) > 0 else 0,
                            'Vagas': vagas
                        })
                
                df_grupos_pdf = pd.DataFrame(grupos_data).sort_values('Programas', ascending=False)
                
                pdf_grupos = gerar_pdf_grupos_sociais(df_filtrado, df_grupos_pdf, area_selecionada)
                
                st.download_button(
                    label="📥 Baixar PDF Grupos",
                    data=pdf_grupos,
                    file_name=f"relatorio_grupos_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                    key='btn_pdf_grupos_download'
                )
                st.success("PDF gerado com sucesso!")
            except Exception as e:
                st.error(f"Erro ao gerar PDF: {str(e)}")

st.markdown("---")

# Relatórios Especializados
st.markdown("## 📋 Relatórios Especializados")

tab1, tab2, tab3 = st.tabs(["📝 Relatório Resumo", "🎯 Apenas com AA", "📊 Análise por Grupos"])

with tab1:
    st.markdown("### Relatório Resumo Executivo")
    st.markdown("Relatório em texto com estatísticas principais")
    
    relatorio_texto = gerar_relatorio_resumo(df_filtrado)
    
    st.text_area(
        "Prévia do Relatório",
        value=relatorio_texto,
        height=400,
        disabled=True
    )
    
    st.download_button(
        label="📥 Download Relatório TXT",
        data=relatorio_texto,
        file_name=f"relatorio_resumo_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
        mime="text/plain",
        use_container_width=True
    )

with tab2:
    st.markdown("### Programas com Editais de AA")
    st.markdown("Apenas programas que possuem editais de ações afirmativas")
    
    df_com_aa = df_filtrado[df_filtrado['Status AA'] == 'Com Editais AA']
    
    st.metric("Total de Programas com AA", len(df_com_aa))
    
    if len(df_com_aa) > 0:
        # Selecionar colunas relevantes
        colunas_aa = [
            'Nome do Programa', 'Sigla da IES', 'UF', 'Região', 'NOTA',
            'Tipo de IES', 'Modalidade de Ensino', 'AA Agregada', 'AA Por Grupo',
            'Qnt. Vagas Totais', 'Vagas Totais AA'
        ]
        colunas_disponiveis = [col for col in colunas_aa if col in df_com_aa.columns]
        
        st.dataframe(df_com_aa[colunas_disponiveis], use_container_width=True, height=300)
        
        col_csv, col_excel = st.columns(2)
        
        with col_csv:
            csv_aa = df_com_aa[colunas_disponiveis].to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📥 CSV - Programas com AA",
                data=csv_aa,
                file_name=f"programas_com_aa_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col_excel:
            excel_aa = to_excel(df_com_aa[colunas_disponiveis], sheet_name='Programas com AA')
            st.download_button(
                label="📥 Excel - Programas com AA",
                data=excel_aa,
                file_name=f"programas_com_aa_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
    else:
        st.warning("Nenhum programa com AA encontrado com os filtros atuais.")

with tab3:
    st.markdown("### Análise por Grupos Sociais")
    st.markdown("Dados agregados sobre grupos contemplados")
    
    from config import GRUPOS_SOCIAIS
    
    # Preparar dados de grupos
    grupos_data = []
    for nome_grupo, coluna in GRUPOS_SOCIAIS.items():
        if coluna in df_filtrado.columns:
            count = (df_filtrado[coluna].fillna('').str.strip().str.upper() == 'SIM').sum()
            grupos_data.append({
                'Grupo': nome_grupo,
                'Programas': count,
                '% do Total': round((count / len(df_filtrado) * 100), 1) if len(df_filtrado) > 0 else 0
            })
    
    df_grupos_export = pd.DataFrame(grupos_data).sort_values('Programas', ascending=False)
    
    st.dataframe(df_grupos_export, use_container_width=True)
    
    col_csv, col_excel = st.columns(2)
    
    with col_csv:
        csv_grupos = df_grupos_export.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="📥 CSV - Análise de Grupos",
            data=csv_grupos,
            file_name=f"analise_grupos_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col_excel:
        excel_grupos = to_excel(df_grupos_export, sheet_name='Análise Grupos')
        st.download_button(
            label="📥 Excel - Análise de Grupos",
            data=excel_grupos,
            file_name=f"analise_grupos_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

st.markdown("---")

# Exportação Completa (Todas as Áreas)
st.markdown("## 🌐 Exportação Completa")
st.markdown("Exporte dados de **todas as áreas** sem filtros")

with st.expander("⚠️ Atenção - Exportação Completa"):
    st.warning("""
    Esta exportação contém **TODOS** os dados de **TODAS** as áreas, sem aplicar filtros.
    O arquivo pode ser grande.
    """)
    
    col_complete_csv, col_complete_excel = st.columns(2)
    
    with col_complete_csv:
        csv_completo = df_todas_areas.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="📥 CSV - Todos os Dados",
            data=csv_completo,
            file_name=f"dados_completos_aa_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col_complete_excel:
        excel_completo = to_excel(df_todas_areas, sheet_name='Todos os Dados')
        st.download_button(
            label="📥 Excel - Todos os Dados",
            data=excel_completo,
            file_name=f"dados_completos_aa_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

st.markdown("---")

# Instruções
st.markdown("## ℹ️ Instruções de Uso")

st.info("""
**Como usar os dados exportados:**

1. **CSV**: Abra com Excel, Google Sheets ou qualquer editor de planilhas
2. **Excel**: Abra diretamente com Microsoft Excel
3. **TXT**: Abra com Notepad, Word ou qualquer editor de texto

**Dicas:**
- Use os filtros na sidebar para refinar os dados antes de exportar
- O nome dos arquivos inclui data e hora da exportação
- Arquivos CSV usam codificação UTF-8 com BOM (compatível com acentos)
""")

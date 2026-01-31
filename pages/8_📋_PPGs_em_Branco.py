"""
📋 Análise de PPGs com Dados Faltantes
Página para visualizar programas com informações incompletas
"""
import streamlit as st
import pandas as pd
from utils.data_loader import load_all_areas


def find_column(df, pattern):
    """Encontra coluna no DataFrame que corresponde ao padrão (case-insensitive, ignorando espaços)"""
    pattern_normalized = pattern.upper().replace(' ', '')
    for col in df.columns:
        if col.upper().replace(' ', '') == pattern_normalized:
            return col
    return None

# Configuração da página
st.set_page_config(
    page_title="PPGs em Branco | Dashboard AA",
    page_icon="📋",
    layout="wide"
)

# Carregar dados
areas_data, df_todas_areas, lista_areas = load_all_areas()

# ==================== CONTEÚDO ====================

st.title("📋 PPGs com Dados Faltantes")
st.markdown("Identificação de programas com informações incompletas")
st.markdown("---")

# Normalizar dados para análise
df = df_todas_areas.copy()

# Encontrar colunas com suporte a múltiplas variações
tipo_ies_col = find_column(df, 'TIPODEIES')
editais_col = find_column(df, 'EDITAISAA')

if tipo_ies_col is None:
    tipo_ies_col = 'Tipo de IES'  # fallback
if editais_col is None:
    editais_col = 'Editais AA'  # fallback

# Tipo de IES
df['Tipo_IES_Normalizado'] = df[tipo_ies_col].fillna('').astype(str).str.strip().str.upper()
df['Tem_Tipo_IES_Válido'] = df['Tipo_IES_Normalizado'].isin(['PUBLICA', 'PRIVADA'])

# Editais AA
df['Editais_AA_Normalizado'] = df[editais_col].fillna('').astype(str).str.strip().str.upper()
df['Tem_Editais_AA_Válido'] = df['Editais_AA_Normalizado'].isin(['SIM', 'NAO', 'NÃO'])

# Criar categorias
st.markdown("## 📊 Resumo de Dados Faltantes")

col1, col2, col3, col4 = st.columns(4)

total_ppgs = len(df)
com_tipo_ies = df['Tem_Tipo_IES_Válido'].sum()
com_editais_aa = df['Tem_Editais_AA_Válido'].sum()
com_ambos = ((df['Tem_Tipo_IES_Válido']) & (df['Tem_Editais_AA_Válido'])).sum()

with col1:
    st.metric("📊 Total de PPGs", f"{total_ppgs}")

with col2:
    st.metric("✅ Com Tipo IES", f"{com_tipo_ies}", delta=f"{100*com_tipo_ies/total_ppgs:.1f}%")

with col3:
    st.metric("✅ Com Editais AA", f"{com_editais_aa}", delta=f"{100*com_editais_aa/total_ppgs:.1f}%")

with col4:
    st.metric("✅ Com Ambos", f"{com_ambos}", delta=f"{100*com_ambos/total_ppgs:.1f}%")

st.markdown("---")

# Filtro por tipo de problema
st.markdown("## 🔍 Filtragem de PPGs com Problemas")

tab1, tab2, tab3 = st.tabs([
    "❌ Sem Tipo de IES",
    "❌ Sem Editais AA", 
    "❌ Com Ambos Faltantes"
])

with tab1:
    df_sem_tipo = df[~df['Tem_Tipo_IES_Válido']].copy()
    st.subheader(f"PPGs sem Tipo de IES válido ({len(df_sem_tipo)} registros)")
    
    if len(df_sem_tipo) > 0:
        cols_to_show = ['Nome do Programa', 'Área', tipo_ies_col, editais_col, 'NOTA']
        cols_to_show = [col for col in cols_to_show if col in df_sem_tipo.columns]
        st.dataframe(
            df_sem_tipo[cols_to_show].sort_values('Área'),
            use_container_width=True,
            hide_index=True
        )
        
        # Download
        csv = df_sem_tipo[cols_to_show].to_csv(index=False)
        st.download_button(
            label="📥 Baixar CSV",
            data=csv,
            file_name="ppgs_sem_tipo_ies.csv",
            mime="text/csv"
        )
    else:
        st.success("✅ Todos os PPGs têm Tipo de IES válido!")

with tab2:
    df_sem_aa = df[~df['Tem_Editais_AA_Válido']].copy()
    st.subheader(f"PPGs sem Editais AA informado ({len(df_sem_aa)} registros)")
    
    if len(df_sem_aa) > 0:
        cols_to_show = ['Nome do Programa', 'Área', tipo_ies_col, editais_col, 'NOTA']
        cols_to_show = [col for col in cols_to_show if col in df_sem_aa.columns]
        st.dataframe(
            df_sem_aa[cols_to_show].sort_values('Área'),
            use_container_width=True,
            hide_index=True
        )
        
        # Download
        csv = df_sem_aa[cols_to_show].to_csv(index=False)
        st.download_button(
            label="📥 Baixar CSV",
            data=csv,
            file_name="ppgs_sem_editais_aa.csv",
            mime="text/csv"
        )
    else:
        st.success("✅ Todos os PPGs têm Editais AA informado!")

with tab3:
    df_ambos = df[(~df['Tem_Tipo_IES_Válido']) & (~df['Tem_Editais_AA_Válido'])].copy()
    st.subheader(f"PPGs com ambos os dados faltantes ({len(df_ambos)} registros)")
    
    if len(df_ambos) > 0:
        cols_to_show = ['Nome do Programa', 'Área', tipo_ies_col, editais_col, 'NOTA']
        cols_to_show = [col for col in cols_to_show if col in df_ambos.columns]
        st.dataframe(
            df_ambos[cols_to_show].sort_values('Área'),
            use_container_width=True,
            hide_index=True
        )
        
        # Download
        csv = df_ambos[cols_to_show].to_csv(index=False)
        st.download_button(
            label="📥 Baixar CSV",
            data=csv,
            file_name="ppgs_ambos_faltantes.csv",
            mime="text/csv"
        )
    else:
        st.success("✅ Todos os PPGs têm dados completos!")

st.markdown("---")

# Análise por área
st.markdown("## 📈 Análise por Área")

resumo_area = pd.DataFrame({
    'Total PPGs': df.groupby('Área').size(),
    'Sem Tipo IES': df.groupby('Área')['Tem_Tipo_IES_Válido'].apply(lambda x: (~x).sum()),
    'Sem Editais AA': df.groupby('Área')['Tem_Editais_AA_Válido'].apply(lambda x: (~x).sum()),
})

resumo_area['% Tipo IES'] = (resumo_area['Total PPGs'] - resumo_area['Sem Tipo IES']) / resumo_area['Total PPGs'] * 100
resumo_area['% Editais AA'] = (resumo_area['Total PPGs'] - resumo_area['Sem Editais AA']) / resumo_area['Total PPGs'] * 100

st.dataframe(resumo_area.round(1), use_container_width=True)

st.markdown("---")
st.markdown("**Legenda:**")
st.markdown("""
- ✅ **Com Tipo IES**: Programas com valor 'Pública' ou 'Privada'
- ✅ **Com Editais AA**: Programas com valor 'SIM' ou 'NÃO'
- ❌ **Sem dados**: Registros vazios, NULL ou valores inválidos
""")

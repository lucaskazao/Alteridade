"""
🏛️ Análise de Universidades com Ações Afirmativas
Página de análise de universidades privadas e públicas com AA
"""
import streamlit as st
import pandas as pd
from utils.data_loader import load_all_areas, prepare_dataframe
from utils.charts import create_ies_type_aa_chart
from config import CORES

# Configuração da página
st.set_page_config(
    page_title="IES e Ações Afirmativas | Dashboard AA",
    page_icon="🏛️",
    layout="wide"
)

# Carregar dados (todas as áreas)
areas_data, df_todas_areas, lista_areas = load_all_areas()

# Preparar dados
df = prepare_dataframe(df_todas_areas.copy())

# ==================== CONTEÚDO ====================

st.title("🏛️ Análise: Universidades com Ações Afirmativas")
st.markdown("Análise geral de todas as áreas sobre presença de Ações Afirmativas em instituições públicas e privadas")
st.markdown("---")

# Criar gráfico (incluindo dados faltantes)
fig, crosstab_data, info = create_ies_type_aa_chart(df, include_invalid=True)

# Exibir gráfico
st.plotly_chart(fig, use_container_width=True)

# Exibir tabela com detalhes
st.markdown("## 📊 Tabela Resumida")

# Criar tabela com totais e percentuais
tabela_resumo = crosstab_data.copy()
tabela_resumo['Total'] = tabela_resumo.sum(axis=1)

# Calcular percentuais para colunas principais
for col in ['Com AA', 'Sem AA']:
    if col in tabela_resumo.columns:
        tabela_resumo[f'% {col}'] = (tabela_resumo[col] / tabela_resumo['Total'] * 100).round(1)

st.dataframe(tabela_resumo, use_container_width=True)

# Exibir métricas principais
st.markdown("## 📈 Métricas Principais")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("📊 Total de PPGs", f"{info['total']}")

with col2:
    st.metric("✅ Com Dados Válidos", f"{info['com_dados']}")

with col3:
    st.metric("⚠️ Com Dados Faltantes", f"{info['sem_dados']}")

with col4:
    pct_cobertura = (info['com_dados'] / info['total'] * 100) if info['total'] > 0 else 0
    st.metric("📋 % Cobertura", f"{pct_cobertura:.1f}%")

# Análise por tipo de IES
st.markdown("## 🔍 Análise Detalhada por Tipo de IES")

col_publica, col_privada = st.columns(2)

with col_publica:
    st.subheader("🏛️ Instituições Públicas")
    st.metric("Com Ações Afirmativas", f"{info['pública_com_aa']:.0f}")
    st.metric("Sem Ações Afirmativas", f"{info['pública_sem_aa']:.0f}")
    total_pub = info['pública_com_aa'] + info['pública_sem_aa']
    if total_pub > 0:
        pct_pub_aa = (info['pública_com_aa'] / total_pub * 100)
        st.metric("% com AA", f"{pct_pub_aa:.1f}%")

with col_privada:
    st.subheader("🏢 Instituições Privadas")
    st.metric("Com Ações Afirmativas", f"{info['privada_com_aa']:.0f}")
    st.metric("Sem Ações Afirmativas", f"{info['privada_sem_aa']:.0f}")
    total_priv = info['privada_com_aa'] + info['privada_sem_aa']
    if total_priv > 0:
        pct_priv_aa = (info['privada_com_aa'] / total_priv * 100)
        st.metric("% com AA", f"{pct_priv_aa:.1f}%")

st.markdown("---")
st.markdown("""
**Nota Importante:**
- Os dados incluem **todas as áreas de conhecimento** do projeto
- 🟢 **Com AA**: Programas que possuem Editais com Ações Afirmativas
- 🔴 **Sem AA**: Programas que não possuem Editais com Ações Afirmativas
- ⚠️ **Dados Faltantes/Inválidos**: Registros sem informação clara sobre Tipo de IES ou Editais AA
""")


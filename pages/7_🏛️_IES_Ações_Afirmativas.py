"""
🏛️ Análise de Universidades com Ações Afirmativas
Página de análise de universidades privadas e públicas com AA
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
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

# Criar 4 gráficos de pizza lado a lado
st.markdown("## 🥧 Distribuição de Ações Afirmativas por Tipo de IES")

col1, col2, col3, col4 = st.columns(4)

# Pizza 1: Instituições Públicas
with col1:
    st.markdown("### 🏛️ Públicas")
    
    if 'Pública' in crosstab_data.index:
        dados_publicas = crosstab_data.loc['Pública']
        labels_pub = []
        values_pub = []
        colors_pub = []
        
        for status, valor in dados_publicas.items():
            if valor > 0:
                labels_pub.append(status)
                values_pub.append(valor)
                if status == 'Com AA':
                    colors_pub.append(CORES['com_aa'])
                elif status == 'Sem AA':
                    colors_pub.append(CORES['sem_aa'])
                else:
                    colors_pub.append(CORES['neutra'])
        
        fig_pub = go.Figure(data=[go.Pie(
            labels=labels_pub,
            values=values_pub,
            marker=dict(colors=colors_pub),
            hole=0.4,
            textposition='inside',
            textinfo='label+value+percent',
            hovertemplate='<b>%{label}</b><br>%{value} PPGs<br>%{percent}<extra></extra>'
        )])
        
        fig_pub.update_layout(
            showlegend=True,
            height=400,
            margin=dict(t=10, b=10, l=10, r=10)
        )
        
        st.plotly_chart(fig_pub, use_container_width=True)
        
        total_pub = dados_publicas.sum()
        st.metric("Total", f"{total_pub:.0f} PPGs")
    else:
        st.info("Sem dados")

# Pizza 2: Instituições Privadas
with col2:
    st.markdown("### 🏢 Privadas")
    
    if 'Privada' in crosstab_data.index:
        dados_privadas = crosstab_data.loc['Privada']
        labels_priv = []
        values_priv = []
        colors_priv = []
        
        for status, valor in dados_privadas.items():
            if valor > 0:
                labels_priv.append(status)
                values_priv.append(valor)
                if status == 'Com AA':
                    colors_priv.append(CORES['com_aa'])
                elif status == 'Sem AA':
                    colors_priv.append(CORES['sem_aa'])
                else:
                    colors_priv.append(CORES['neutra'])
        
        fig_priv = go.Figure(data=[go.Pie(
            labels=labels_priv,
            values=values_priv,
            marker=dict(colors=colors_priv),
            hole=0.4,
            textposition='inside',
            textinfo='label+value+percent',
            hovertemplate='<b>%{label}</b><br>%{value} PPGs<br>%{percent}<extra></extra>'
        )])
        
        fig_priv.update_layout(
            showlegend=True,
            height=400,
            margin=dict(t=10, b=10, l=10, r=10)
        )
        
        st.plotly_chart(fig_priv, use_container_width=True)
        
        total_priv = dados_privadas.sum()
        st.metric("Total", f"{total_priv:.0f} PPGs")
    else:
        st.info("Sem dados")

# Pizza 3: Dados Faltantes/Inválidos
with col3:
    st.markdown("### ⚠️ Dados Faltantes")
    
    if 'Dados Faltantes/Inválidos' in crosstab_data.index:
        dados_faltantes = crosstab_data.loc['Dados Faltantes/Inválidos']
        labels_falt = []
        values_falt = []
        colors_falt = []
        
        for status, valor in dados_faltantes.items():
            if valor > 0:
                labels_falt.append(status)
                values_falt.append(valor)
                if status == 'Com AA':
                    colors_falt.append(CORES['com_aa'])
                elif status == 'Sem AA':
                    colors_falt.append(CORES['sem_aa'])
                else:
                    colors_falt.append(CORES['neutra'])
        
        fig_falt = go.Figure(data=[go.Pie(
            labels=labels_falt,
            values=values_falt,
            marker=dict(colors=colors_falt),
            hole=0.4,
            textposition='inside',
            textinfo='label+value+percent',
            hovertemplate='<b>%{label}</b><br>%{value} PPGs<br>%{percent}<extra></extra>'
        )])
        
        fig_falt.update_layout(
            showlegend=True,
            height=400,
            margin=dict(t=10, b=10, l=10, r=10)
        )
        
        st.plotly_chart(fig_falt, use_container_width=True)
        
        total_falt = dados_faltantes.sum()
        st.metric("Total", f"{total_falt:.0f} PPGs")
    else:
        st.info("Sem dados")

# Pizza 4: Composição de quem TEM AA (Pública vs Privada)
with col4:
    st.markdown("### 📊 Composição Com AA")
    
    # Pegar apenas dados "Com AA" de públicas e privadas
    valores_com_aa = []
    labels_com_aa = []
    colors_com_aa = []
    
    if 'Pública' in crosstab_data.index and 'Com AA' in crosstab_data.columns:
        val_pub = crosstab_data.loc['Pública', 'Com AA']
        if val_pub > 0:
            valores_com_aa.append(val_pub)
            labels_com_aa.append('Pública')
            colors_com_aa.append(CORES['primaria'])
    
    if 'Privada' in crosstab_data.index and 'Com AA' in crosstab_data.columns:
        val_priv = crosstab_data.loc['Privada', 'Com AA']
        if val_priv > 0:
            valores_com_aa.append(val_priv)
            labels_com_aa.append('Privada')
            colors_com_aa.append(CORES['secundaria'])
    
    if valores_com_aa:
        fig_composicao = go.Figure(data=[go.Pie(
            labels=labels_com_aa,
            values=valores_com_aa,
            marker=dict(colors=colors_com_aa),
            hole=0.4,
            textposition='inside',
            textinfo='label+value+percent',
            hovertemplate='<b>%{label}</b><br>%{value} PPGs<br>%{percent}<extra></extra>'
        )])
        
        fig_composicao.update_layout(
            showlegend=True,
            height=400,
            margin=dict(t=10, b=10, l=10, r=10)
        )
        
        st.plotly_chart(fig_composicao, use_container_width=True)
        
        total_com_aa = sum(valores_com_aa)
        st.metric("Total Com AA", f"{total_com_aa:.0f} PPGs")
    else:
        st.info("Sem dados")

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
st.markdown("## 🔍 Resumo Comparativo")

col_publica, col_privada = st.columns(2)

with col_publica:
    st.subheader("🏛️ Instituições Públicas")
    
    total_pub = info['pública_com_aa'] + info['pública_sem_aa']
    if total_pub > 0:
        pct_pub_aa = (info['pública_com_aa'] / total_pub * 100)
        st.metric("Com AA", f"{info['pública_com_aa']:.0f}", delta=f"{pct_pub_aa:.1f}%")
        st.metric("Sem AA", f"{info['pública_sem_aa']:.0f}", delta=f"{100-pct_pub_aa:.1f}%")
    else:
        st.info("Sem dados de instituições públicas")

with col_privada:
    st.subheader("🏢 Instituições Privadas")
    
    total_priv = info['privada_com_aa'] + info['privada_sem_aa']
    if total_priv > 0:
        pct_priv_aa = (info['privada_com_aa'] / total_priv * 100)
        st.metric("Com AA", f"{info['privada_com_aa']:.0f}", delta=f"{pct_priv_aa:.1f}%")
        st.metric("Sem AA", f"{info['privada_sem_aa']:.0f}", delta=f"{100-pct_priv_aa:.1f}%")
    else:
        st.info("Sem dados de instituições privadas")

st.markdown("---")
st.markdown("""
**Nota Importante:**
- Os dados incluem **todas as áreas de conhecimento** do projeto
- 🟢 **Com AA**: Programas que possuem Editais com Ações Afirmativas
- 🔴 **Sem AA**: Programas que não possuem Editais com Ações Afirmativas
- ⚠️ **Dados Faltantes/Inválidos**: Registros sem informação clara sobre Tipo de IES ou Editais AA
""")


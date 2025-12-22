"""
🔄 Comparador de Programas
Página para comparação lado a lado de programas de pós-graduação
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.data_loader import load_all_areas, get_data_for_area, prepare_dataframe
from utils.filters import render_area_selector, render_global_filters
from utils.pdf_generator import gerar_pdf_comparacao
from config import GRUPOS_SOCIAIS, CORES

# Configuração da página
st.set_page_config(
    page_title="Comparador | Dashboard AA",
    page_icon="🔄",
    layout="wide"
)

# Carregar dados
areas_data, df_todas_areas, lista_areas = load_all_areas()

# Sidebar
st.sidebar.markdown("# 🔄 Comparador")
st.sidebar.markdown("Compare programas lado a lado")
st.sidebar.markdown("---")

# Seletor de Área
area_selecionada = render_area_selector(lista_areas)

# Obter dados
df = get_data_for_area(area_selecionada, areas_data, df_todas_areas)
df = prepare_dataframe(df)

# ==================== CONTEÚDO ====================

st.title("🔄 Comparador de Programas")
st.markdown("Utilize os filtros abaixo para encontrar e selecionar os programas que deseja comparar.")
st.markdown("---")

# --- Filtros de Busca no Corpo da Página ---
with st.expander("🔍 Filtros de Busca", expanded=True):
    st.info("Selecione as características para filtrar a lista de programas disponíveis.")
    
    col_f1, col_f2, col_f3 = st.columns(3)
    col_f4, col_f5 = st.columns(2)
    
    df_filtrado = df.copy()
    
    # 1. Filtro de Área (se estiver vendo todas)
    with col_f1:
        if 'Área' in df.columns and area_selecionada == 'Todas as Áreas':
            areas_disp = sorted(df['Área'].unique().tolist())
            sel_area = st.multiselect("Área do Conhecimento:", areas_disp)
            if sel_area:
                df_filtrado = df_filtrado[df_filtrado['Área'].isin(sel_area)]
        else:
            st.markdown(f"**Área:** {area_selecionada}")
            
    # 2. Filtro de Região
    with col_f2:
        if 'Região' in df.columns:
            regioes = sorted(df_filtrado['Região'].dropna().unique().tolist())
            sel_regiao = st.multiselect("Região:", regioes)
            if sel_regiao:
                df_filtrado = df_filtrado[df_filtrado['Região'].isin(sel_regiao)]

    # 3. Filtro de Estado (UF)
    with col_f3:
        if 'UF' in df.columns:
            ufs_disponiveis = sorted(df_filtrado['UF'].dropna().unique().tolist())
            sel_uf = st.multiselect("Estado (UF):", ufs_disponiveis)
            if sel_uf:
                df_filtrado = df_filtrado[df_filtrado['UF'].isin(sel_uf)]

    # 4. Filtro de IES
    with col_f4:
        if 'Sigla da IES' in df.columns:
            ies_disponiveis = sorted(df_filtrado['Sigla da IES'].dropna().unique().tolist())
            sel_ies = st.multiselect("Sigla da IES:", ies_disponiveis)
            if sel_ies:
                df_filtrado = df_filtrado[df_filtrado['Sigla da IES'].isin(sel_ies)]

    # 5. Filtro de Nota
    with col_f5:
        if 'NOTA' in df.columns:
            notas_disponiveis = sorted(df_filtrado['NOTA'].dropna().unique().tolist())
            sel_nota = st.multiselect("Nota CAPES:", notas_disponiveis)
            if sel_nota:
                df_filtrado = df_filtrado[df_filtrado['NOTA'].isin(sel_nota)]

    st.markdown(f"**Resultados encontrados:** {len(df_filtrado)} programas")

st.markdown("---")

# Inicializar estado da seleção se não existir
if 'comparador_programas' not in st.session_state:
    st.session_state.comparador_programas = []

# --- Área de Seleção de Programas ---
st.markdown("### ➕ Adicionar Programas")

col_add1, col_add2 = st.columns([3, 1])

programas_filtrados = sorted(df_filtrado['Nome do Programa'].unique().tolist())

with col_add1:
    # Seletor de candidato (apenas um por vez, da lista filtrada)
    candidato_selecionado = st.selectbox(
        f"Escolha um programa da lista filtrada ({len(programas_filtrados)} opções):",
        options=['Selecione um programa...'] + programas_filtrados,
        index=0,
        key="candidato_selecionado"
    )

with col_add2:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("➕ Adicionar", use_container_width=True):
        if candidato_selecionado != 'Selecione um programa...':
            if candidato_selecionado not in st.session_state.comparador_programas:
                if len(st.session_state.comparador_programas) < 4:
                    st.session_state.comparador_programas.append(candidato_selecionado)
                    st.success(f"Adicionado: {candidato_selecionado}")
                    st.rerun()
                else:
                    st.warning("Máximo de 4 programas atingido.")
            else:
                st.warning("Programa já adicionado.")
        else:
            st.warning("Selecione um programa válido.")

st.markdown("---")

# --- Lista de Comparação (Bucket) ---
st.markdown("### 📋 Programas Selecionados para Comparação")

# Função callback para remover itens
def atualizar_selecao():
    st.session_state.comparador_programas = st.session_state.bucket_selecao

programas_selecionados = st.multiselect(
    "Gerencie sua lista de comparação (remova itens clicando no X):",
    options=st.session_state.comparador_programas,
    default=st.session_state.comparador_programas,
    key="bucket_selecao",
    on_change=atualizar_selecao
)

col_actions1, col_actions2 = st.columns([3, 1])

with col_actions2:
    if st.button("🗑️ Limpar Tudo", use_container_width=True):
        st.session_state.comparador_programas = []
        st.rerun()

# Atualizar a variável principal para o resto do script
programas_selecionados = st.session_state.comparador_programas

# Verificar seleção
if len(programas_selecionados) < 2:
    st.info("👋 Adicione pelo menos **2 programas** para iniciar a comparação.")
    
    # Mostrar sugestão/exemplo se nada selecionado
    if len(programas_selecionados) == 0:
        if st.button("🎲 Carregar Exemplo Aleatório"):
            import random
            # Tentar pegar um com AA e um sem AA se possível
            com_aa = df[df['Status AA'] == 'Com Editais AA']['Nome do Programa'].tolist()
            sem_aa = df[df['Status AA'] == 'Sem Editais AA']['Nome do Programa'].tolist()
            
            exemplo = []
            if com_aa: exemplo.append(random.choice(com_aa))
            if sem_aa: exemplo.append(random.choice(sem_aa))
            
            # Completar se faltar
            todos_progs = df['Nome do Programa'].unique().tolist()
            while len(exemplo) < 2 and len(todos_progs) > len(exemplo):
                prog = random.choice(todos_progs)
                if prog not in exemplo:
                    exemplo.append(prog)
            
            # Atualizar estado e recarregar
            st.session_state.comparador_programas = exemplo
            st.rerun()

else:
    # Filtrar dados para os programas selecionados
    df_comp = df[df['Nome do Programa'].isin(programas_selecionados)].copy()
    
    # Ordenar conforme a seleção do usuário (para manter a ordem visual)
    df_comp['Nome do Programa'] = pd.Categorical(df_comp['Nome do Programa'], categories=programas_selecionados, ordered=True)
    df_comp = df_comp.sort_values('Nome do Programa')
    
    # --- Tabela Comparativa ---
    st.markdown("## 📋 Tabela Comparativa")
    
    # Definir colunas para comparação
    cols_info = ['Sigla da IES', 'UF', 'Região', 'NOTA', 'Tipo de IES', 'Modalidade de Ensino']
    cols_aa = ['Status AA', 'AA Agregada', 'AA Por Grupo']
    cols_vagas = ['Qnt. Vagas Totais', 'Vagas Totais AA']
    
    todas_cols = cols_info + cols_aa + cols_vagas
    
    # Preparar dados garantindo alinhamento
    comp_data = {col: [] for col in todas_cols if col in df_comp.columns}
    
    for prog in programas_selecionados:
        # Pegar a primeira ocorrência do programa (caso haja duplicatas no nome)
        row = df_comp[df_comp['Nome do Programa'] == prog].iloc[0]
        for col in comp_data.keys():
            comp_data[col].append(row[col])
            
    df_view = pd.DataFrame(comp_data, index=programas_selecionados).T
    
    # Estilizar a tabela
    st.dataframe(df_view, use_container_width=True)
    
    # --- Gráficos Comparativos ---
    st.markdown("---")
    st.markdown("## 📊 Visualização Comparativa")
    
    col_graf1, col_graf2 = st.columns(2)
    
    with col_graf1:
        # Gráfico de Vagas
        if 'Qnt. Vagas Totais' in df_comp.columns and 'Vagas Totais AA' in df_comp.columns:
            # Preparar dados para plot
            vagas_data = []
            for _, row in df_comp.iterrows():
                total = pd.to_numeric(row['Qnt. Vagas Totais'], errors='coerce') or 0
                aa = pd.to_numeric(row['Vagas Totais AA'], errors='coerce') or 0
                regular = total - aa
                
                vagas_data.append({'Programa': row['Nome do Programa'], 'Tipo': 'Vagas Regulares', 'Qtd': regular})
                vagas_data.append({'Programa': row['Nome do Programa'], 'Tipo': 'Vagas AA', 'Qtd': aa})
            
            df_vagas = pd.DataFrame(vagas_data)
            
            fig_vagas = px.bar(
                df_vagas, 
                x='Programa', 
                y='Qtd', 
                color='Tipo',
                title='Distribuição de Vagas (Total vs AA)',
                color_discrete_map={'Vagas AA': CORES['com_aa'], 'Vagas Regulares': CORES['neutra']},
                barmode='stack'
            )
            fig_vagas.update_layout(legend=dict(orientation="h", y=1.1))
            st.plotly_chart(fig_vagas, use_container_width=True)
            
    with col_graf2:
        # Gráfico Radar (se houver métricas numéricas suficientes ou criar scores)
        # Vamos criar um "Score de Inclusão" baseado em presença de grupos
        
        radar_data = []
        categorias = ['Pretos/Pardos', 'Indígenas', 'PcD', 'Quilombolas', 'Trans']
        cols_map = {
            'Pretos/Pardos': 'AA Pretos e Pardos',
            'Indígenas': 'AA Indígena',
            'PcD': 'AA PCd',
            'Quilombolas': 'AA Quilombola',
            'Trans': 'AA Trans.'
        }
        
        fig_radar = go.Figure()
        
        for prog in programas_selecionados:
            row = df_comp[df_comp['Nome do Programa'] == prog].iloc[0]
            valores = []
            
            for cat in categorias:
                col = cols_map[cat]
                if col in df_comp.columns:
                    val = 1 if str(row[col]).strip().upper() == 'SIM' else 0
                else:
                    val = 0
                valores.append(val)
            
            # Fechar o ciclo
            valores_plot = valores + [valores[0]]
            cats_plot = categorias + [categorias[0]]
            
            fig_radar.add_trace(go.Scatterpolar(
                r=valores_plot,
                theta=cats_plot,
                fill='toself',
                name=prog
            ))
            
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1.1],
                    tickvals=[0, 1],
                    ticktext=['Não', 'Sim']
                )
            ),
            title="Cobertura de Grupos Principais",
            showlegend=True,
            legend=dict(orientation="h", y=-0.1)
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    # --- Matriz de Grupos Sociais ---
    st.markdown("---")
    st.markdown("## 👥 Matriz de Grupos Sociais")
    
    # Preparar matriz
    grupos_matrix = []
    colunas_grupos = []
    
    for nome_grupo, col_db in GRUPOS_SOCIAIS.items():
        if col_db in df_comp.columns:
            colunas_grupos.append(nome_grupo)
            linha = {'Grupo': nome_grupo}
            for prog in programas_selecionados:
                row = df_comp[df_comp['Nome do Programa'] == prog].iloc[0]
                val = str(row[col_db]).strip().upper()
                linha[prog] = "✅ Sim" if val == 'SIM' else "❌ Não"
            grupos_matrix.append(linha)
            
    if grupos_matrix:
        df_matrix = pd.DataFrame(grupos_matrix)
        st.dataframe(
            df_matrix,
            column_config={
                "Grupo": st.column_config.TextColumn("Grupo Social", width="medium"),
            },
            use_container_width=True,
            hide_index=True
        )
    else:
        st.warning("Dados de grupos sociais não disponíveis para comparação.")

    # --- Exportação ---
    st.markdown("---")
    st.markdown("## 📥 Exportar Comparação")
    
    col_exp1, col_exp2, col_exp3 = st.columns(3)
    
    with col_exp1:
        # CSV
        csv = df_comp.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="📥 Baixar CSV",
            data=csv,
            file_name="comparacao_programas.csv",
            mime="text/csv",
            use_container_width=True
        )
        
    with col_exp2:
        # Excel
        from io import BytesIO
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_comp.to_excel(writer, sheet_name='Comparação', index=False)
        
        st.download_button(
            label="📥 Baixar Excel",
            data=output.getvalue(),
            file_name="comparacao_programas.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
        
    with col_exp3:
        # PDF
        try:
            pdf_buffer = gerar_pdf_comparacao(df_comp, area_selecionada)
            st.download_button(
                label="📄 Baixar Relatório PDF",
                data=pdf_buffer,
                file_name="relatorio_comparativo.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"Erro ao gerar PDF: {str(e)}")
            st.info("Verifique se as bibliotecas necessárias estão instaladas (reportlab).")

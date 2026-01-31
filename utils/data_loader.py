"""
Módulo de carregamento de dados para o Dashboard de Ações Afirmativas
"""
import pandas as pd
import streamlit as st


def find_column(df, pattern):
    """
    Encontra coluna no DataFrame que corresponde ao padrão (case-insensitive, ignorando espaços)
    
    Args:
        df: DataFrame
        pattern: padrão a procurar (ex: 'TIPODEIES', 'EDITAISAA')
        
    Returns:
        str: nome da coluna ou None se não encontrar
    """
    pattern_normalized = pattern.upper().replace(' ', '')
    for col in df.columns:
        if col.upper().replace(' ', '') == pattern_normalized:
            return col
    return None

@st.cache_data
def load_all_areas():
    """
    Carrega todas as áreas do arquivo dados_brutos.xlsx com normalização de valores
    
    Returns:
        tuple: (areas_data, df_todas_areas, lista_areas)
            - areas_data: dict com DataFrames por área
            - df_todas_areas: DataFrame agregado
            - lista_areas: lista de nomes das áreas
    """
    excel_file = pd.ExcelFile('dados_brutos.xlsx')
    areas_data = {}
    
    # Carregar cada aba/área
    for sheet_name in excel_file.sheet_names:
        df_area = pd.read_excel(excel_file, sheet_name=sheet_name)
        df_area['Área'] = sheet_name  # Adicionar coluna identificando a área
        
        # Normalizar valores das colunas (mantendo nomes originais)
        # Para 'Tipo de IES' ou 'TIPO DE IES' - encontrar e normalizar qualquer variação
        for col_name in df_area.columns:
            if col_name.upper().replace(' ', '') == 'TIPODEIES':
                df_area[col_name] = df_area[col_name].fillna('').astype(str).str.strip().str.upper()
            # Para 'Editais AA'
            elif col_name.upper().replace(' ', '') == 'EDITAISAA':
                df_area[col_name] = df_area[col_name].fillna('').astype(str).str.strip().str.upper()
            # Para NOTA/Nota/NOTAS
            elif col_name.upper() == 'NOTA' or col_name.upper() == 'NOTAS':
                df_area[col_name] = df_area[col_name].astype(str).str.strip()
        
        areas_data[sheet_name] = df_area
    
    # Criar DataFrame agregado com todas as áreas
    df_todas_areas = pd.concat(areas_data.values(), ignore_index=True)
    
    return areas_data, df_todas_areas, list(excel_file.sheet_names)
    
    # Criar DataFrame agregado com todas as áreas
    df_todas_areas = pd.concat(areas_data.values(), ignore_index=True)
    
    return areas_data, df_todas_areas, list(excel_file.sheet_names)


def get_data_for_area(area_selecionada, areas_data, df_todas_areas):
    """
    Retorna dados da área selecionada
    
    Args:
        area_selecionada: nome da área ou 'Todas as Áreas'
        areas_data: dict com DataFrames por área
        df_todas_areas: DataFrame agregado
        
    Returns:
        DataFrame da área selecionada
    """
    if area_selecionada == 'Todas as Áreas':
        return df_todas_areas.copy()
    else:
        return areas_data[area_selecionada].copy()


def get_filtered_data(df, area_selecionada, areas_data, df_todas_areas):
    """
    Retorna dados filtrados pela área selecionada
    
    Args:
        df: DataFrame original
        area_selecionada: nome da área ou 'Todas as Áreas'
        areas_data: dict com dados por área
        df_todas_areas: DataFrame com todas as áreas
        
    Returns:
        DataFrame filtrado
    """
    if area_selecionada == 'Todas as Áreas':
        return df_todas_areas.copy()
    else:
        return areas_data[area_selecionada].copy()


def prepare_dataframe(df):
    """
    Prepara DataFrame com transformações padrão
    
    Args:
        df: DataFrame a ser preparado
        
    Returns:
        DataFrame preparado
    """
    df = df.copy()
    
    # Procurar a coluna de Editais AA (pode ser 'Editais AA' ou 'EDITAIS_AA' ou outra variação)
    editais_col = None
    for col in df.columns:
        if col.upper().replace(' ', '') == 'EDITAISAA':
            editais_col = col
            break
    
    if editais_col is not None:
        # Classificar programas com/sem AA
        df['Status AA'] = df[editais_col].apply(
            lambda x: 'Com Editais AA' if str(x).upper() == 'SIM' else 'Sem Editais AA'
        )
    
    return df


def get_available_columns(df, column_type='all'):
    """
    Retorna colunas disponíveis para análise
    
    Args:
        df: DataFrame
        column_type: 'all', 'categorical', 'numerical'
        
    Returns:
        list: lista de nomes de colunas
    """
    if column_type == 'categorical':
        return df.select_dtypes(include=['object']).columns.tolist()
    elif column_type == 'numerical':
        return df.select_dtypes(include=['number']).columns.tolist()
    else:
        return df.columns.tolist()


def validate_dataframe(df):
    """
    Valida estrutura do DataFrame
    
    Args:
        df: DataFrame a validar
        
    Returns:
        tuple: (is_valid, list_of_missing_columns)
    """
    required_columns = [
        'Nome do Programa',
        'Sigla da IES',
        'UF',
        'Região',
        'NOTA',
        'Editais AA'
    ]
    
    missing_columns = [col for col in required_columns if col not in df.columns]
    is_valid = len(missing_columns) == 0
    
    return is_valid, missing_columns


def get_summary_stats(df):
    """
    Calcula estatísticas resumidas dos dados
    
    Args:
        df: DataFrame com dados
        
    Returns:
        dict: dicionário com estatísticas
    """
    stats = {
        'total_programas': len(df),
        'com_aa': 0,
        'sem_aa': 0,
        'percentual_aa': 0.0,
        'total_vagas': 0,
        'total_vagas_aa': 0,
        'areas_unicas': 0,
        'regioes_unicas': 0,
        'ufs_unicas': 0
    }
    
    if len(df) > 0:
        # Programas com/sem AA - procurar coluna de Editais AA
        editais_col = None
        for col in df.columns:
            if col.upper().replace(' ', '') == 'EDITAISAA':
                editais_col = col
                break
        
        if editais_col is not None:
            stats['com_aa'] = df[editais_col].str.upper().eq('SIM').sum()
            stats['sem_aa'] = stats['total_programas'] - stats['com_aa']
            stats['percentual_aa'] = (stats['com_aa'] / stats['total_programas'] * 100) if stats['total_programas'] > 0 else 0
        
        # Vagas
        if 'Qnt. Vagas Totais' in df.columns:
            stats['total_vagas'] = int(pd.to_numeric(df['Qnt. Vagas Totais'], errors='coerce').fillna(0).sum())
        
        if 'Vagas Totais AA' in df.columns:
            stats['total_vagas_aa'] = int(pd.to_numeric(df['Vagas Totais AA'], errors='coerce').fillna(0).sum())
        
        # Diversidade
        if 'Área' in df.columns:
            stats['areas_unicas'] = df['Área'].nunique()
        
        if 'Região' in df.columns:
            stats['regioes_unicas'] = df['Região'].nunique()
        
        if 'UF' in df.columns:
            stats['ufs_unicas'] = df['UF'].nunique()
    
    return stats


def initialize_session_state():
    """
    Inicializa variáveis de estado da sessão para persistência de dados
    """
    if 'data_loaded' not in st.session_state:
        st.session_state.data_loaded = False
    
    if 'areas_data' not in st.session_state:
        st.session_state.areas_data = {}
    
    if 'df_todas_areas' not in st.session_state:
        st.session_state.df_todas_areas = pd.DataFrame()
    
    if 'lista_areas' not in st.session_state:
        st.session_state.lista_areas = []
    
    if 'area_selecionada' not in st.session_state:
        st.session_state.area_selecionada = 'Todas as Áreas'


def load_data_into_session():
    """
    Carrega dados na sessão (deve ser chamado uma vez no início)
    """
    if not st.session_state.data_loaded:
        areas_data, df_todas_areas, lista_areas = load_all_areas()
        
        st.session_state.areas_data = areas_data
        st.session_state.df_todas_areas = df_todas_areas
        st.session_state.lista_areas = lista_areas
        st.session_state.data_loaded = True

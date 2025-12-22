"""
Configurações globais do dashboard
"""

# Mapeamento de grupos sociais
GRUPOS_SOCIAIS = {
    'Pretos e Pardos': 'AA Pretos e Pardos',
    'PcD': 'AA PCd',
    'Indígenas': 'AA Indigena',
    'Quilombolas': 'AA Quilombola',
    'Refugiados': 'AA Refugiados e Humanitários',
    'Trans': 'AA Trans',
    'Ciganos': 'AA Ciganos',
    'Pop. Ribeirinha': 'AA Pop Ribeirinha',
    'Outros': 'Outros grupos'
}

# Ordem padrão das notas
ORDEM_NOTAS = ['A', '3', '4', '5', '6', '7']

# Cores padrão para gráficos
CORES = {
    'com_aa': '#2ecc71',
    'sem_aa': '#e74c3c',
    'primaria': '#3498db',
    'secundaria': '#f39c12',
    'terciaria': '#9b59b6',
    'neutra': '#95a5a6'
}

# Colunas de vagas
COLUNAS_VAGAS = {
    'total': 'Qnt Vagas Totais',
    'aa_total': 'Vagas Totais AA',
    'agregadas': 'Vagas Totais Agregadas',
    'por_grupo': 'Vagas Totais Por Grupo/Exclusivas'
}

# Configuração da página
PAGE_CONFIG = {
    'page_title': 'Dashboard Ações Afirmativas - CAPES',
    'page_icon': '📊',
    'layout': 'wide',
    'initial_sidebar_state': 'expanded'
}

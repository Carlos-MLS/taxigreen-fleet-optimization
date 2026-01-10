"""
Configurações globais do sistema TaxiGreen.
Define parâmetros de simulação, custos e pesos da função objetivo.
"""

# ============================================================
# CONFIGURAÇÕES DA FROTA
# ============================================================

# Veículos Elétricos
ELECTRIC_VEHICLE_CONFIG = {
    'autonomia_min': 150.0,      # km
    'autonomia_max': 300.0,      # km
    'capacidade': 4,             # passageiros
    'custo_km_min': 0.10,        # €/km
    'custo_km_max': 0.15,        # €/km
    'tempo_recarga_min': 30.0,   # minutos
    'tempo_recarga_max': 60.0,   # minutos
    'emissoes_co2': 0.0,         # kg CO2/km (localmente)
}

# Veículos a Combustão
COMBUSTION_VEHICLE_CONFIG = {
    'autonomia_min': 500.0,      # km
    'autonomia_max': 700.0,      # km
    'capacidade': 4,             # passageiros
    'custo_km_min': 0.20,        # €/km
    'custo_km_max': 0.30,        # €/km
    'tempo_abastecimento_min': 5.0,   # minutos
    'tempo_abastecimento_max': 10.0,  # minutos
    'emissoes_co2_min': 0.120,   # kg CO2/km
    'emissoes_co2_max': 0.180,   # kg CO2/km
}

# Composição inicial da frota (exemplo)
FROTA_INICIAL = {
    'num_eletricos': 6,
    'num_combustao': 4,
}

# ============================================================
# CONFIGURAÇÕES DA CIDADE
# ============================================================

CITY_CONFIG = {
    'num_nodes': 50,             # Número de localizações
    'velocidade_media': 40.0,    # km/h (para calcular tempos)
    'densidade_conexoes': 0.3,   # Percentagem de conexões possíveis
}

# ============================================================
# CONFIGURAÇÕES DE TRÂNSITO
# ============================================================

TRAFFIC_CONFIG = {
    # Fatores de trânsito por período do dia
    'periodos': {
        'madrugada': (0, 6),      # 00:00 - 06:00
        'manha': (6, 9),          # 06:00 - 09:00 (rush)
        'dia': (9, 17),           # 09:00 - 17:00
        'tarde': (17, 20),        # 17:00 - 20:00 (rush)
        'noite': (20, 24),        # 20:00 - 24:00
    },
    'fatores': {
        'madrugada': 1.0,         # Tráfego livre
        'manha': 2.5,             # Rush matinal
        'dia': 1.5,               # Moderado
        'tarde': 2.8,             # Rush vespertino (pior)
        'noite': 1.2,             # Leve
    },
}

# ============================================================
# CONFIGURAÇÕES DE EVENTOS DINÂMICOS
# ============================================================

DYNAMIC_EVENTS_CONFIG = {
    # Probabilidade de eventos por hora de simulação
    'prob_estrada_cortada': 0.02,     # 2% por hora
    'prob_falha_estacao': 0.01,       # 1% por hora
    
    # Duração dos eventos (minutos)
    'duracao_corte_min': 15.0,
    'duracao_corte_max': 120.0,
    'duracao_falha_min': 30.0,
    'duracao_falha_max': 180.0,
}

# ============================================================
# CONFIGURAÇÕES DE PEDIDOS
# ============================================================

REQUEST_CONFIG = {
    # Taxa de chegada de pedidos (por hora)
    'taxa_pedidos_baixa': 5,     # Períodos calmos
    'taxa_pedidos_media': 15,    # Períodos normais
    'taxa_pedidos_alta': 30,     # Períodos de pico
    
    # Distribuição de prioridades
    'prob_normal': 0.70,         # 70% pedidos normais
    'prob_urgente': 0.20,        # 20% pedidos urgentes
    'prob_premium': 0.10,        # 10% pedidos premium
    
    # Distribuição de preferência ambiental
    'prob_prefere_eletrico': 0.30,    # 30% preferem elétrico
    'prob_indiferente': 0.60,         # 60% indiferentes
    'prob_nao_prefere': 0.10,         # 10% não preferem
    
    # Número de passageiros
    'passageiros_min': 1,
    'passageiros_max': 4,
    'prob_1_passageiro': 0.40,
    'prob_2_passageiros': 0.30,
    'prob_3_passageiros': 0.20,
    'prob_4_passageiros': 0.10,
    
    # Tempo de espera máximo (minutos)
    'tempo_espera_max_default': 15.0,
}

# ============================================================
# CONFIGURAÇÕES DE CUSTOS E FUNÇÃO OBJETIVO
# ============================================================

COST_CONFIG = {
    # Pesos da função objetivo (devem somar ~1.0)
    'peso_custo_operacional': 0.30,
    'peso_tempo_resposta': 0.25,
    'peso_ambiental': 0.15,
    'peso_ineficiencia': 0.15,
    'peso_penalizacoes': 0.10,
    'peso_bonificacoes': 0.05,
    
    # Custos específicos
    'custo_co2_por_kg': 0.05,          # €/kg CO2
    'penalizacao_km_vazio': 1.5,       # Multiplicador
    'custo_tempo_parado': 0.20,        # €/min
    
    # Penalizações por rejeição (multiplicador pelo peso prioridade)
    'penalizacao_rejeicao_base': 50.0,  # €
    
    # Bonificações
    'bonus_ocupacao_alta': 10.0,       # € (se > 80% ocupação)
    'bonus_sustentabilidade': 5.0,     # € por viagem elétrica
}

# ============================================================
# CONFIGURAÇÕES DE SIMULAÇÃO
# ============================================================

SIMULATION_CONFIG = {
    'duracao_simulacao': 1440,   # minutos (24 horas)
    'passo_tempo': 1.0,          # minutos por iteração
    'tempo_embarque': 2.0,       # minutos
    'tempo_desembarque': 1.5,    # minutos
    'limiar_recarga_urgente': 0.20,  # 20% autonomia
    'seed_aleatoria': 42,        # Para reprodutibilidade
}

# ============================================================
# CONFIGURAÇÕES DE ALGORITMOS
# ============================================================

ALGORITHM_CONFIG = {
    # A* e heurísticas
    'peso_heuristica': 1.0,      # Peso da heurística no A*
    
    # Limites de busca
    'max_nos_expandidos': 10000,
    'timeout_busca': 30.0,       # segundos
}

# ============================================================
# CONFIGURAÇÕES DE OUTPUT E LOGGING
# ============================================================

OUTPUT_CONFIG = {
    'verbose': True,
    'salvar_metricas': True,
    'intervalo_log': 60,         # minutos (log a cada hora)
    'diretorio_resultados': 'results/',
    'formato_timestamp': '%Y%m%d_%H%M%S',
}

# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def obter_fator_transito(hora: float) -> float:
    """
    Retorna o fator de trânsito para uma determinada hora.
    
    Args:
        hora: Hora do dia (0-24)
        
    Returns:
        Fator de trânsito
    """
    hora_int = int(hora) % 24
    
    for periodo, (inicio, fim) in TRAFFIC_CONFIG['periodos'].items():
        if inicio <= hora_int < fim:
            return TRAFFIC_CONFIG['fatores'][periodo]
    
    return 1.0  # Default


def obter_taxa_pedidos(hora: float) -> int:
    """
    Retorna a taxa de pedidos por hora para um determinado momento.
    
    Args:
        hora: Hora do dia (0-24)
        
    Returns:
        Taxa de pedidos por hora
    """
    hora_int = int(hora) % 24
    
    # Períodos de pico: manhã (7-9) e tarde (17-20)
    if 7 <= hora_int < 9 or 17 <= hora_int < 20:
        return REQUEST_CONFIG['taxa_pedidos_alta']
    # Períodos calmos: madrugada (0-6) e noite (22-24)
    elif 0 <= hora_int < 6 or 22 <= hora_int < 24:
        return REQUEST_CONFIG['taxa_pedidos_baixa']
    # Períodos normais: resto do dia
    else:
        return REQUEST_CONFIG['taxa_pedidos_media']


def validar_configuracoes():
    """Valida se as configurações são consistentes."""
    # Verificar se pesos somam aproximadamente 1.0
    soma_pesos = sum([
        COST_CONFIG['peso_custo_operacional'],
        COST_CONFIG['peso_tempo_resposta'],
        COST_CONFIG['peso_ambiental'],
        COST_CONFIG['peso_ineficiencia'],
        COST_CONFIG['peso_penalizacoes'],
        COST_CONFIG['peso_bonificacoes'],
    ])
    
    if abs(soma_pesos - 1.0) > 0.01:
        print(f"AVISO: Soma dos pesos = {soma_pesos:.2f} (esperado ~1.0)")
    
    return True


# Validar ao importar
if __name__ != "__main__":
    validar_configuracoes()

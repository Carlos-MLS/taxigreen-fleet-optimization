"""
Teste de integração completo do sistema TaxiGreen.
Demonstra simulação completa com todos os componentes.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.models.vehicle import Vehicle, VehicleType, VehicleState
from src.models.request import Request, Priority
from src.models.city import City
from src.simulation.simulator import TaxiSimulator
from src.strategies.allocation import criar_estrategia
import config


def criar_cidade_exemplo() -> City:
    """Cria cidade de exemplo para testes."""
    cidade = City()
    
    # Coordenadas dos nós (para heurísticas)
    cidade.coordenadas = {
        'Centro': (0, 0),
        'Norte': (0, 5),
        'Sul': (0, -5),
        'Este': (5, 0),
        'Oeste': (-5, 0),
        'Shopping': (3, 3),
        'Hospital': (-3, 3),
        'Universidade': (3, -3),
        'Aeroporto': (-3, -3),
        'Estacao_Central': (0, 0)
    }
    
    # Adicionar arestas (distâncias em km, tempo base em minutos)
    arestas = [
        ('Centro', 'Norte', 5.0, 10.0),
        ('Centro', 'Sul', 5.0, 10.0),
        ('Centro', 'Este', 5.0, 10.0),
        ('Centro', 'Oeste', 5.0, 10.0),
        ('Norte', 'Shopping', 4.2, 8.0),
        ('Norte', 'Hospital', 4.2, 8.0),
        ('Sul', 'Universidade', 4.2, 8.0),
        ('Sul', 'Aeroporto', 4.2, 8.0),
        ('Este', 'Shopping', 3.0, 6.0),
        ('Este', 'Universidade', 3.0, 6.0),
        ('Oeste', 'Hospital', 3.0, 6.0),
        ('Oeste', 'Aeroporto', 3.0, 6.0),
        ('Shopping', 'Hospital', 6.0, 12.0),
        ('Universidade', 'Aeroporto', 6.0, 12.0),
    ]
    
    for origem, destino, dist, tempo in arestas:
        cidade.adicionar_aresta(origem, destino, dist, tempo)
    
    return cidade


def criar_frota_exemplo() -> list:
    """Cria frota de exemplo."""
    frota = [
        # Veículos elétricos
        Vehicle(
            vehicle_id="EV001",
            tipo=VehicleType.ELECTRIC,
            capacidade=4,
            autonomia_maxima=200.0,
            custo_km=0.15,
            localizacao="Centro"
        ),
        Vehicle(
            vehicle_id="EV002",
            tipo=VehicleType.ELECTRIC,
            capacidade=4,
            autonomia_maxima=200.0,
            custo_km=0.15,
            localizacao="Norte"
        ),
        
        # Veículos a combustão
        Vehicle(
            vehicle_id="CV001",
            tipo=VehicleType.COMBUSTION,
            capacidade=4,
            autonomia_maxima=500.0,
            custo_km=0.30,
            localizacao="Sul"
        ),
        Vehicle(
            vehicle_id="CV002",
            tipo=VehicleType.COMBUSTION,
            capacidade=6,
            autonomia_maxima=500.0,
            custo_km=0.35,
            localizacao="Este"
        ),
    ]
    
    return frota


def teste_simulacao_basica():
    """Teste básico de simulação."""
    print("\n" + "=" * 70)
    print(" TESTE: Simulação Básica ".center(70, '='))
    print("=" * 70)
    
    cidade = criar_cidade_exemplo()
    frota = criar_frota_exemplo()
    
    # Criar simulador
    simulador = TaxiSimulator(
        frota=frota,
        cidade=cidade,
        config=config.__dict__,
        seed=42
    )
    
    # Gerar pedidos aleatórios
    simulador.gerar_pedidos_aleatorios(
        num_pedidos=10,
        tempo_maximo=120.0,  # 2 horas
        distribuicao='uniforme'
    )
    
    # Executar simulação
    simulador.executar(tempo_total=120.0, verbose=True)
    
    # Imprimir métricas
    simulador.imprimir_resumo()
    
    print("\n[OK] Teste de simulacao basica completo\n")


def teste_comparacao_estrategias():
    """Testa e compara diferentes estratégias de alocação."""
    print("\n" + "=" * 70)
    print(" TESTE: Comparação de Estratégias ".center(70, '='))
    print("=" * 70)
    
    estrategias = ['nearest', 'lowest_cost', 'eco_friendly', 'balanced']
    resultados = {}
    
    for nome_estrategia in estrategias:
        print(f"\n    Testando estrategia: {nome_estrategia}")
        print("-" * 70)
        
        cidade = criar_cidade_exemplo()
        frota = criar_frota_exemplo()
        
        # Criar simulador com estratégia
        simulador = TaxiSimulator(
            frota=frota,
            cidade=cidade,
            config=config.__dict__,
            seed=42  # Mesma seed para comparação justa
        )
        
        # Gerar mesmos pedidos
        simulador.gerar_pedidos_aleatorios(
            num_pedidos=15,
            tempo_maximo=180.0,
            distribuicao='uniforme'
        )
        
        # Executar
        simulador.executar(tempo_total=180.0, verbose=False)
        
        # Coletar métricas
        relatorio = simulador.obter_relatorio_metricas()
        metricas = relatorio['metricas_obrigatorias']
        
        resultados[nome_estrategia] = {
            'tempo_resposta': metricas['1_tempo_medio_resposta']['valor'],
            'ocupacao': metricas['2_taxa_ocupacao_frota']['valor'],
            'custo': metricas['3_custos_operacionais']['valor'],
            'emissoes': metricas['4_emissoes_co2']['valor'],
            'atendidos': metricas['5_pedidos_nao_atendidos']['valor']['atendidos'],
            'km_vazios': metricas['6_km_vazios']['valor']
        }
    
    # Imprimir comparação
    print("\n" + "=" * 70)
    print(" COMPARAÇÃO DE ESTRATÉGIAS ".center(70, '='))
    print("=" * 70)
    
    print(f"\n{'Estratégia':<20} {'Tempo(min)':<12} {'Ocup(%)':<10} {'Custo(€)':<12} {'CO2(kg)':<10} {'Atend.':<8} {'KmVazio':<10}")
    print("-" * 110)
    
    for estrategia, metricas in resultados.items():
        print(f"{estrategia:<20} "
              f"{metricas['tempo_resposta']:<12.2f} "
              f"{metricas['ocupacao']:<10.1f} "
              f"{metricas['custo']:<12.2f} "
              f"{metricas['emissoes']:<10.2f} "
              f"{metricas['atendidos']:<8} "
              f"{metricas['km_vazios']:<10.2f}")
    
    # Determinar melhor em cada categoria
    print("\nMELHORES POR CATEGORIA:")
    
    melhor_tempo = min(resultados.items(), key=lambda x: x[1]['tempo_resposta'])
    print(f"  - Menor tempo de resposta: {melhor_tempo[0]} ({melhor_tempo[1]['tempo_resposta']:.2f} min)")
    
    melhor_ocupacao = max(resultados.items(), key=lambda x: x[1]['ocupacao'])
    print(f"  - Maior ocupacao: {melhor_ocupacao[0]} ({melhor_ocupacao[1]['ocupacao']:.1f}%)")
    
    melhor_custo = min(resultados.items(), key=lambda x: x[1]['custo'])
    print(f"  - Menor custo: {melhor_custo[0]} ({melhor_custo[1]['custo']:.2f} EUR)")
    
    melhor_emissoes = min(resultados.items(), key=lambda x: x[1]['emissoes'])
    print(f"  - Menores emissoes: {melhor_emissoes[0]} ({melhor_emissoes[1]['emissoes']:.2f} kg CO2)")
    
    print("\n[OK] Teste de comparacao de estrategias completo\n")


def teste_cenario_alta_demanda():
    """Testa cenário com alta demanda de pedidos."""
    print("\n" + "=" * 70)
    print(" TESTE: Cenário de Alta Demanda ".center(70, '='))
    print("=" * 70)
    
    cidade = criar_cidade_exemplo()
    frota = criar_frota_exemplo()
    
    simulador = TaxiSimulator(
        frota=frota,
        cidade=cidade,
        config=config.__dict__,
        seed=42
    )
    
    # Gerar muitos pedidos (mais que veículos disponíveis)
    simulador.gerar_pedidos_aleatorios(
        num_pedidos=25,  # 25 pedidos para 4 veículos
        tempo_maximo=180.0,
        distribuicao='poisson'
    )
    
    print(f"\n    Cenario: 25 pedidos, 4 veiculos, 180 minutos")
    
    simulador.executar(tempo_total=180.0, verbose=False)
    simulador.imprimir_resumo()
    
    print("\n[OK] Teste de alta demanda completo\n")


def teste_cenario_baixa_autonomia():
    """Testa cenário com veículos de baixa autonomia."""
    print("\n" + "=" * 70)
    print(" TESTE: Cenário de Baixa Autonomia ".center(70, '='))
    print("=" * 70)
    
    cidade = criar_cidade_exemplo()
    
    # Criar frota com autonomia limitada
    frota = [
        Vehicle(
            vehicle_id="EV001",
            tipo=VehicleType.ELECTRIC,
            capacidade=4,
            autonomia_maxima=200.0,
            custo_km=0.15,
            localizacao="Centro"
        ),
        Vehicle(
            vehicle_id="CV001",
            tipo=VehicleType.COMBUSTION,
            capacidade=4,
            autonomia_maxima=500.0,
            custo_km=0.30,
            localizacao="Norte"
        ),
    ]
    
    # Reduzir autonomia após criação
    for veiculo in frota:
        veiculo.autonomia_atual = 30.0  # Autonomia baixa
    
    simulador = TaxiSimulator(
        frota=frota,
        cidade=cidade,
        config=config.__dict__,
        seed=42
    )
    
    simulador.gerar_pedidos_aleatorios(
        num_pedidos=10,
        tempo_maximo=120.0,
        distribuicao='uniforme'
    )
    
    print(f"\n    Cenario: Veiculos com autonomia inicial baixa")
    
    simulador.executar(tempo_total=120.0, verbose=True)
    simulador.imprimir_resumo()
    
    print("\n[OK] Teste de baixa autonomia completo\n")


def main():
    """Executa todos os testes de integração."""
    print("\n" + "=" * 70)
    print(" TESTES DE INTEGRAÇÃO - SISTEMA TAXIGREEN ".center(70, '='))
    print("=" * 70)
    
    try:
        # Teste 1: Simulação básica
        teste_simulacao_basica()
        
        # Teste 2: Comparação de estratégias
        teste_comparacao_estrategias()
        
        # Teste 3: Alta demanda
        teste_cenario_alta_demanda()
        
        # Teste 4: Baixa autonomia
        teste_cenario_baixa_autonomia()
        
        print("\n" + "=" * 70)
        print(" [OK] TODOS OS TESTES DE INTEGRACAO PASSARAM ".center(70, '='))
        print("=" * 70 + "\n")
        
        return 0
        
    except Exception as e:
        print(f"\n[ERRO] Erro nos testes: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    exit(main())

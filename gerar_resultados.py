"""
Script para gerar resultados experimentais completos.
Executa múltiplas simulações e exporta métricas para análise.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.models.vehicle import Vehicle, VehicleType
from src.models.request import Request, Priority
from src.models.city import City
from src.simulation.simulator import TaxiSimulator
from src.strategies.allocation import criar_estrategia
import config
import json
from datetime import datetime


def criar_cidade_padrao() -> City:
    """Cria cidade padrão para experimentos."""
    cidade = City()
    
    # Coordenadas (grid 10x10)
    cidade.coordenadas = {
        f'N{i}': (i % 10, i // 10) for i in range(50)
    }
    
    # Adicionar arestas principais
    for i in range(50):
        # Conexões horizontais
        if (i + 1) % 10 != 0:
            cidade.adicionar_aresta(f'N{i}', f'N{i+1}', 1.0, 2.0)
        # Conexões verticais
        if i + 10 < 50:
            cidade.adicionar_aresta(f'N{i}', f'N{i+10}', 1.0, 2.0)
        # Diagonais principais
        if (i + 11) < 50 and (i + 11) % 10 != 0:
            cidade.adicionar_aresta(f'N{i}', f'N{i+11}', 1.4, 3.0)
    
    return cidade


def criar_frota_padrao() -> list:
    """Cria frota padrão para experimentos."""
    frota = []
    
    # 3 veículos elétricos
    for i in range(3):
        frota.append(Vehicle(
            vehicle_id=f'EV{i+1:03d}',
            tipo=VehicleType.ELECTRIC,
            localizacao=f'N{i*10}',
            autonomia_maxima=250.0,
            capacidade=4,
            custo_km=0.12
        ))
    
    # 2 veículos a combustão
    for i in range(2):
        frota.append(Vehicle(
            vehicle_id=f'CV{i+1:03d}',
            tipo=VehicleType.COMBUSTION,
            localizacao=f'N{(i+3)*10}',
            autonomia_maxima=600.0,
            capacidade=4,
            custo_km=0.25
        ))
    
    return frota


def executar_experimento(
    nome: str,
    cidade: City,
    frota: list,
    estrategia: str,
    num_pedidos: int,
    tempo_total: float,
    seed: int = 42
) -> dict:
    """
    Executa um experimento completo.
    
    Returns:
        Dicionário com métricas
    """
    print(f"\n{'='*70}")
    print(f"EXPERIMENTO: {nome}")
    print(f"Estratégia: {estrategia}")
    print(f"Pedidos: {num_pedidos}, Tempo: {tempo_total}min")
    print(f"{'='*70}\n")
    
    # Criar simulador
    config_sim = {
        'tempo_recarga_eletrico': 45.0,
        'tempo_recarga_combustao': 10.0,
        'limiar_recarga': 0.2
    }
    
    estrategia_func = criar_estrategia(estrategia, cidade)
    
    simulador = TaxiSimulator(
        frota=frota,
        cidade=cidade,
        config=config_sim,
        estrategia_alocacao=estrategia_func,
        seed=seed
    )
    
    # Gerar pedidos
    simulador.gerar_pedidos_aleatorios(num_pedidos, tempo_total)
    
    # Executar simulação
    simulador.executar(tempo_total, verbose=False)
    
    # Obter métricas
    relatorio = simulador.obter_relatorio_metricas()
    
    # Adicionar informações do experimento
    resultado = {
        'experimento': nome,
        'estrategia': estrategia,
        'num_pedidos': num_pedidos,
        'tempo_total': tempo_total,
        'timestamp': datetime.now().isoformat(),
        'metricas': relatorio
    }
    
    # Imprimir resumo
    m_obrig = relatorio['metricas_obrigatorias']
    m_naoa = m_obrig['5_pedidos_nao_atendidos']['valor']
    
    print("\nRESUMO:")
    print(f"  Tempo Medio Resposta: {m_obrig['1_tempo_medio_resposta']['valor']:.2f} min")
    print(f"  Taxa Ocupacao: {m_obrig['2_taxa_ocupacao_frota']['valor']:.2f}%")
    print(f"  Custos: {m_obrig['3_custos_operacionais']['valor']:.2f} EUR")
    print(f"  Emissoes: {m_obrig['4_emissoes_co2']['valor']:.2f} kg CO2")
    print(f"  Atendidos: {m_naoa['atendidos']}/{m_naoa['total']}")
    print(f"  Km Vazios: {m_obrig['6_km_vazios']['valor']:.2f} km")
    
    return resultado


def main():
    """Executa bateria completa de experimentos."""
    
    print("="*70)
    print("GERAÇÃO DE RESULTADOS EXPERIMENTAIS - TAXIGREEN")
    print("="*70)
    
    # Criar ambiente comum
    cidade = criar_cidade_padrao()
    
    resultados = []
    
    #  Comparação de Estratégias
    print("\n\n SÉRIE 1: COMPARAÇÃO DE ESTRATÉGIAS \n")
    
    estrategias = ['nearest', 'lowest_cost', 'eco_friendly']
    
    for estrategia in estrategias:
        frota = criar_frota_padrao()  # Nova frota para cada teste
        resultado = executar_experimento(
            nome=f"Estratégia: {estrategia}",
            cidade=cidade,
            frota=frota,
            estrategia=estrategia,
            num_pedidos=30,
            tempo_total=180.0,
            seed=42
        )
        resultados.append(resultado)
    
    # EXPERIMENTO 2: Diferentes Volumes de Demanda 
    print("\n\n SÉRIE 2: DIFERENTES VOLUMES DE DEMANDA \n")
    
    volumes = [
        (10, 60.0, "Baixa Demanda"),
        (30, 180.0, "Demanda Média"),
        (50, 300.0, "Alta Demanda")
    ]
    
    for num_pedidos, tempo, nome in volumes:
        frota = criar_frota_padrao()
        resultado = executar_experimento(
            nome=nome,
            cidade=cidade,
            frota=frota,
            estrategia='lowest_cost',
            num_pedidos=num_pedidos,
            tempo_total=tempo,
            seed=42
        )
        resultados.append(resultado)
    
    # EXPERIMENTO 3: Diferentes Composições de Frota
    print("\n\nSÉRIE 3: COMPOSIÇÕES DE FROTA \n")
    
    composicoes = [
        ("Só Elétricos", 5, 0),
        ("Só Combustão", 0, 5),
        ("Mista Equilibrada", 3, 2)
    ]
    
    for nome_comp, num_ev, num_cv in composicoes:
        # Criar frota específica
        frota = []
        for i in range(num_ev):
            frota.append(Vehicle(
                vehicle_id=f'EV{i+1:03d}',
                tipo=VehicleType.ELECTRIC,
                localizacao=f'N{i*10}',
                autonomia_maxima=250.0,
                capacidade=4,
                custo_km=0.12
            ))
        for i in range(num_cv):
            frota.append(Vehicle(
                vehicle_id=f'CV{i+1:03d}',
                tipo=VehicleType.COMBUSTION,
                localizacao=f'N{(i+num_ev)*10}',
                autonomia_maxima=600.0,
                capacidade=4,
                custo_km=0.25
            ))
        
        resultado = executar_experimento(
            nome=f"Frota: {nome_comp}",
            cidade=cidade,
            frota=frota,
            estrategia='lowest_cost',
            num_pedidos=25,
            tempo_total=150.0,
            seed=42
        )
        resultados.append(resultado)
    
    # EXPORTAR RESULTADOS 
    
    output_dir = "resultados"
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Exportar JSON completo
    json_file = f"{output_dir}/resultados_{timestamp}.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(resultados, f, indent=2, ensure_ascii=False)
    
    print(f"\n\n{'='*70}")
    print("RESULTADOS EXPORTADOS")
    print(f"{'='*70}")
    print(f"Arquivo JSON: {json_file}")
    print(f"Total de experimentos: {len(resultados)}")
    
    # Criar tabela comparativa simples
    print(f"\n\n{'='*70}")
    print("TABELA COMPARATIVA - ESTRATÉGIAS")
    print(f"{'='*70}")
    print(f"{'Estratégia':<20} {'Resposta':<12} {'Ocupação':<10} {'Custos':<10} {'Emissões':<10} {'Atendidos':<10}")
    print("-"*70)
    
    for r in resultados[:4]:  # Primeiros 4 (estratégias)
        m = r['metricas']['metricas_obrigatorias']
        m_naoa = m['5_pedidos_nao_atendidos']['valor']
        print(f"{r['estrategia']:<20} "
              f"{m['1_tempo_medio_resposta']['valor']:>8.2f}min "
              f"{m['2_taxa_ocupacao_frota']['valor']:>8.2f}% "
              f"{m['3_custos_operacionais']['valor']:>8.2f}€ "
              f"{m['4_emissoes_co2']['valor']:>8.2f}kg "
              f"{m_naoa['atendidos']:>3}/{m_naoa['total']:<3}")
    
    print(f"\n{'='*70}\n")
    
    return resultados


if __name__ == "__main__":
    resultados = main()
    print("\nGeracao de resultados completa.\n")

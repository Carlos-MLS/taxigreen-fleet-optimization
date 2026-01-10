"""
TaxiGreen - Sistema de Gestão Inteligente de Frota
Trabalho de Inteligência Artificial 2024/2025

Ponto de entrada principal do sistema.
"""

import sys
sys.path.append('src')

from models import (
    Vehicle, VehicleType, VehicleState,
    Request, Priority, EnvironmentalPreference,
    Station, StationType,
    City
)
import config


def criar_frota_exemplo():
    """Cria uma frota de exemplo para testes."""
    frota = []
    
    # Criar veículos elétricos
    for i in range(config.FROTA_INICIAL['num_eletricos']):
        veiculo = Vehicle(
            vehicle_id=f"E{i+1:03d}",
            tipo=VehicleType.ELECTRIC,
            localizacao=f"N{(i % 10) + 1}",  # Distribuir pela cidade
            autonomia_maxima=250.0,
            capacidade=4,
            custo_km=0.12
        )
        frota.append(veiculo)
    
    # Criar veículos a combustão
    for i in range(config.FROTA_INICIAL['num_combustao']):
        veiculo = Vehicle(
            vehicle_id=f"C{i+1:03d}",
            tipo=VehicleType.COMBUSTION,
            localizacao=f"N{(i % 10) + 1}",
            autonomia_maxima=600.0,
            capacidade=4,
            custo_km=0.25
        )
        frota.append(veiculo)
    
    return frota


def criar_cidade_exemplo():
    """Cria uma cidade de exemplo para testes."""
    city = City()
    
    # Criar uma pequena rede de teste (10 nós)
    conexoes = [
        ("N1", "N2", 5.0),
        ("N2", "N3", 3.0),
        ("N3", "N4", 4.0),
        ("N4", "N5", 6.0),
        ("N1", "N6", 7.0),
        ("N6", "N7", 4.0),
        ("N7", "N8", 5.0),
        ("N8", "N9", 3.0),
        ("N9", "N10", 4.0),
        ("N5", "N10", 8.0),
        ("N3", "N7", 6.0),
        ("N4", "N8", 5.0),
    ]
    
    for origem, destino, distancia in conexoes:
        city.adicionar_aresta(origem, destino, distancia)
    
    return city


def criar_estacoes_exemplo():
    """Cria estações de exemplo."""
    estacoes = []
    
    # Estações de recarga elétrica
    estacoes.append(Station("ER1", StationType.ELECTRIC_CHARGING, "N3", tempo_servico=45.0, capacidade=2))
    estacoes.append(Station("ER2", StationType.ELECTRIC_CHARGING, "N7", tempo_servico=45.0, capacidade=2))
    
    # Postos de combustível
    estacoes.append(Station("PC1", StationType.FUEL_STATION, "N5", tempo_servico=7.5, capacidade=3))
    estacoes.append(Station("PC2", StationType.FUEL_STATION, "N9", tempo_servico=7.5, capacidade=3))
    
    return estacoes


def criar_pedidos_exemplo():
    """Cria alguns pedidos de exemplo para testes."""
    pedidos = [
        Request("P001", "N1", "N10", 2, 0.0, Priority.NORMAL, EnvironmentalPreference.YES),
        Request("P002", "N2", "N8", 1, 5.0, Priority.URGENT, EnvironmentalPreference.INDIFFERENT),
        Request("P003", "N6", "N4", 3, 10.0, Priority.PREMIUM, EnvironmentalPreference.NO),
        Request("P004", "N3", "N9", 2, 15.0, Priority.NORMAL, EnvironmentalPreference.YES),
        Request("P005", "N7", "N5", 4, 20.0, Priority.URGENT, EnvironmentalPreference.INDIFFERENT),
    ]
    return pedidos


def exibir_estado_sistema(frota, cidade, estacoes, pedidos):
    """Exibe o estado atual do sistema."""
    print("\n" + "=" * 70)
    print("  ESTADO DO SISTEMA TAXIGREEN")
    print("=" * 70)
    
    # Frota
    print(f"\n    FROTA ({len(frota)} veiculos)")
    print("-" * 70)
    eletricos = [v for v in frota if v.tipo == VehicleType.ELECTRIC]
    combustao = [v for v in frota if v.tipo == VehicleType.COMBUSTION]
    print(f"  Elétricos: {len(eletricos)} | Combustão: {len(combustao)}")
    
    for v in frota[:3]:  # Mostrar apenas primeiros 3
        print(f"  • {v}")
    if len(frota) > 3:
        print(f"  ... e mais {len(frota) - 3} veículos")
    
    # Cidade
    print(f"\n    CIDADE")
    print("-" * 70)
    print(f"  {cidade}")
    
    # Estações
    print(f"\n    ESTACOES ({len(estacoes)})")
    print("-" * 70)
    for e in estacoes:
        print(f"  • {e}")
    
    # Pedidos
    print(f"\n    PEDIDOS ({len(pedidos)})")
    print("-" * 70)
    for p in pedidos:
        print(f"  • {p}")
    
    print("\n" + "=" * 70)


def main():
    """Função principal."""
    print("\n" + "-" * 70)
    print("  SISTEMA TAXIGREEN - GESTAO INTELIGENTE DE FROTA")
    print("  Trabalho de Inteligencia Artificial 2024/2025")
    print("-" * 70)
    
    # Criar componentes do sistema
    print("\n    A inicializar sistema...")
    
    frota = criar_frota_exemplo()
    cidade = criar_cidade_exemplo()
    estacoes = criar_estacoes_exemplo()
    pedidos = criar_pedidos_exemplo()
    
    print("[OK] Sistema inicializado com sucesso!")
    
    # Exibir estado
    exibir_estado_sistema(frota, cidade, estacoes, pedidos)
    
    # Demonstração de funcionalidade básica
    print("\n    DEMONSTRACAO DE FUNCIONALIDADES")
    print("=" * 70)
    
    # 1. Verificar se veículo pode aceitar pedido
    veiculo = frota[0]
    pedido = pedidos[0]
    
    print(f"\n[1] Verificar compatibilidade:")
    print(f"   Veículo: {veiculo.id} ({veiculo.tipo.value})")
    print(f"   Pedido: {pedido.id} ({pedido.origem}→{pedido.destino})")
    
    # Calcular distância estimada (exemplo simplificado)
    distancia_estimada = 50.0  # km (em sistema real, usar algoritmo de busca)
    pode_aceitar = veiculo.pode_aceitar_pedido(pedido.num_passageiros, distancia_estimada)
    
    print(f"   - Pode aceitar? {pode_aceitar}")
    print(f"   - Prefere eletrico? {pedido.prefere_eletrico()}")
    print(f"   - Tipos compativeis? {pedido.prefere_eletrico() == (veiculo.tipo == VehicleType.ELECTRIC)}")
    
    # 2. Simular atribuição
    if pode_aceitar:
        print(f"\n[2] Atribuir veiculo ao pedido:")
        pedido.atribuir_veiculo(veiculo.id, tempo_atual=0.0)
        veiculo.estado = VehicleState.TRAVELING
        print(f"   - Pedido {pedido.id} atribuido a {veiculo.id}")
        print(f"   - Status pedido: {pedido.status.value}")
        print(f"   - Estado veiculo: {veiculo.estado.value}")
    
    # 3. Verificar necessidade de recarga
    print(f"\n[3] Verificar autonomia:")
    for v in frota[:3]:
        precisa = v.precisa_recarga()
        print(f"   {v.id}: {v.autonomia_atual:.0f}/{v.autonomia_maxima:.0f}km - Recarga? {'SIM' if precisa else 'NAO'}")
    
    # 4. Verificar estações disponíveis
    print(f"\n[4] Estacoes disponiveis:")
    for e in estacoes:
        status = "LIVRE" if e.esta_disponivel() else "OCUPADA"
        print(f"   {e.id} ({e.tipo.value}): {status}")
    
    # 5. Informações de trânsito
    print(f"\n[5] Condicoes de transito:")
    hora_atual = 8.0  # 8:00 (rush matinal)
    fator = config.obter_fator_transito(hora_atual)
    taxa_pedidos = config.obter_taxa_pedidos(hora_atual)
    print(f"   Hora: {hora_atual:.0f}:00")
    print(f"   Fator transito: {fator}x (1.0 = livre, 3.0 = congestionamento)")
    print(f"   Taxa pedidos: ~{taxa_pedidos} pedidos/hora")
    
    print("\n" + "-" * 70)
    print("DEMONSTRACAO CONCLUIDA")
    print("-" * 70)
    
    print("\n")


if __name__ == "__main__":
    main()

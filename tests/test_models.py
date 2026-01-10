"""
Script de teste simples para validar as classes base.
"""

import sys
sys.path.append('src')

from models import (
    Vehicle, VehicleType, VehicleState,
    Request, Priority, EnvironmentalPreference,
    Station, StationType,
    City
)


def testar_veiculo():
    """Testa a classe Vehicle."""
    print("=" * 50)
    print("TESTE: Classe Vehicle")
    print("=" * 50)
    
    # Criar veículo elétrico
    v1 = Vehicle(
        vehicle_id="V001",
        tipo=VehicleType.ELECTRIC,
        localizacao="N1",
        autonomia_maxima=250.0,
        capacidade=4,
        custo_km=0.12
    )
    
    print(f"\n    Veiculo criado: {v1}")
    print(f"  - Pode aceitar 3 passageiros com 50km? {v1.pode_aceitar_pedido(3, 50)}")
    print(f"  - Precisa recarga? {v1.precisa_recarga()}")
    
    # Consumir autonomia
    v1.consumir_autonomia(100, com_passageiros=True)
    print(f"\n    Apos viajar 100km:")
    print(f"  - Autonomia restante: {v1.autonomia_atual:.1f}km")
    print(f"  - Emissões: {v1.calcular_emissoes(100):.2f}kg CO2")
    print(f"  - Km percorridos: {v1.km_percorridos:.1f}km")
    
    # Criar veículo combustão
    v2 = Vehicle(
        vehicle_id="V002",
        tipo=VehicleType.COMBUSTION,
        localizacao="N5",
        autonomia_maxima=600.0,
        capacidade=4,
        custo_km=0.25
    )
    
    print(f"\n    Veiculo combustao criado: {v2}")
    print(f"  - Tempo recarga estimado: {v2.tempo_recarga_estimado():.1f} min")
    print(f"  - Emissões (100km): {v2.calcular_emissoes(100):.2f}kg CO2")


def testar_pedido():
    """Testa a classe Request."""
    print("\n" + "=" * 50)
    print("TESTE: Classe Request")
    print("=" * 50)
    
    # Criar pedido
    p1 = Request(
        request_id="P001",
        origem="N1",
        destino="N10",
        num_passageiros=2,
        horario_pedido=0.0,
        prioridade=Priority.URGENT,
        preferencia_ambiental=EnvironmentalPreference.YES
    )
    
    print(f"\n    Pedido criado: {p1}")
    print(f"  - Peso prioridade: {p1.peso_prioridade()}")
    print(f"  - Prefere elétrico? {p1.prefere_eletrico()}")
    
    # Simular atribuição
    p1.atribuir_veiculo("V001", tempo_atual=2.0)
    print(f"\n    Apos atribuicao:")
    print(f"  - Status: {p1.status.value}")
    print(f"  - Veículo: {p1.veiculo_atribuido}")
    print(f"  - Tempo resposta: {p1.tempo_resposta():.1f} min")


def testar_estacao():
    """Testa a classe Station."""
    print("\n" + "=" * 50)
    print("TESTE: Classe Station")
    print("=" * 50)
    
    # Criar estação
    e1 = Station(
        station_id="E001",
        tipo=StationType.ELECTRIC_CHARGING,
        localizacao="N15",
        tempo_servico=45.0,
        capacidade=2
    )
    
    print(f"\n    Estacao criada: {e1}")
    print(f"  - Disponível? {e1.esta_disponivel()}")
    
    # Aceitar veículos
    aceite1 = e1.aceitar_veiculo("V001")
    aceite2 = e1.aceitar_veiculo("V002")
    aceite3 = e1.aceitar_veiculo("V003")  # Deve falhar (capacidade = 2)
    
    print(f"\n    Apos aceitar veiculos:")
    print(f"  - Veículo 1 aceite? {aceite1}")
    print(f"  - Veículo 2 aceite? {aceite2}")
    print(f"  - Veículo 3 aceite? {aceite3} (capacidade cheia)")
    print(f"  - Status: {e1.disponibilidade.value}")
    
    # Libertar veículo
    e1.libertar_veiculo("V001")
    print(f"\n    Apos libertar V001:")
    print(f"  - Status: {e1.disponibilidade.value}")
    print(f"  - Total atendimentos: {e1.total_atendimentos}")


def testar_cidade():
    """Testa a classe City."""
    print("\n" + "=" * 50)
    print("TESTE: Classe City")
    print("=" * 50)
    
    # Criar cidade
    city = City()
    
    # Adicionar arestas (cria nós automaticamente)
    city.adicionar_aresta("N1", "N2", distancia=5.0, tempo_base=10.0)
    city.adicionar_aresta("N2", "N3", distancia=3.0, tempo_base=6.0)
    city.adicionar_aresta("N1", "N3", distancia=7.0, tempo_base=12.0)
    city.adicionar_aresta("N3", "N4", distancia=4.0, tempo_base=8.0)
    
    print(f"\n    Cidade criada: {city}")
    print(f"  - Nós: {list(city.nodes)}")
    
    # Testar vizinhos
    vizinhos_n1 = city.obter_vizinhos("N1")
    print(f"\n    Vizinhos de N1: {vizinhos_n1}")
    
    # Testar caminho
    existe = city.existe_caminho("N1", "N2")
    print(f"  - Existe caminho N1→N2? {existe}")
    
    # Obter aresta
    edge = city.obter_aresta("N1", "N2")
    if edge:
        print(f"\n    Aresta N1-N2:")
        print(f"  - Distância: {edge.distancia}km")
        print(f"  - Tempo base: {edge.tempo_base} min")
        print(f"  - Tempo atual: {edge.tempo_viagem()} min")
    
    # Atualizar trânsito
    city.atualizar_transito_global(2.0)  # Congestionamento
    print(f"\n    Apos atualizar transito (fator 2.0):")
    print(f"  - Tempo N1→N2: {edge.tempo_viagem()} min")
    
    # Cortar estrada
    city.cortar_estrada("N1", "N2", duracao=30.0)
    print(f"\n    Apos cortar estrada N1-N2:")
    print(f"  - Caminho existe? {city.existe_caminho('N1', 'N2')}")
    print(f"  - Tempo: {edge.tempo_viagem()} min (infinito)")


def main():
    """Executa todos os testes."""
    print("\n" + "=" * 50)
    print("  TESTES DAS CLASSES BASE - TaxiGreen")
    print("=" * 50)
    
    try:
        testar_veiculo()
        testar_pedido()
        testar_estacao()
        testar_cidade()
        
        print("\n" + "=" * 50)
        print("[OK] TODOS OS TESTES CONCLUIDOS COM SUCESSO!")
        print("=" * 50 + "\n")
        
    except Exception as e:
        print(f"\n[ERRO] durante testes: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

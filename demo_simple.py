"""
Demonstração simples do sistema TaxiGreen.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.models.vehicle import Vehicle, VehicleType
from src.models.request import Request, Priority
from src.models.city import City


def main():
    """Demonstracao simples."""
    print("\n" + "=" * 70)
    print(" DEMONSTRACAO SISTEMA TAXIGREEN ".center(70, '='))
    print("=" * 70)
    
    # Criar cidade
    print("\n[1] Criando cidade...")
    cidade = City()
    cidade.coordenadas = {
        'Centro': (0, 0),
        'Norte': (0, 5),
        'Sul': (0, -5)
    }
    cidade.adicionar_aresta('Centro', 'Norte', 5.0, 10.0)
    cidade.adicionar_aresta('Centro', 'Sul', 5.0, 10.0)
    print(f"   Cidade com {len(cidade.nodes)} nos criada")
    
    # Criar frota
    print("\n[2] Criando frota...")
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
        )
    ]
    print(f"   Frota com {len(frota)} veiculos criada")
    
    # Criar pedido
    print("\n[3] Criando pedido...")
    pedido = Request(
        request_id="REQ001",
        origem="Centro",
        destino="Norte",
        num_passageiros=2,
        horario_pedido=0.0,
        prioridade=Priority.NORMAL
    )
    print(f"   Pedido {pedido.id}: {pedido.origem} -> {pedido.destino}")
    
    # Mostrar estado
    print("\n[4] Estado atual:")
    for veiculo in frota:
        print(f"   {veiculo.id} ({veiculo.tipo.value})")
        print(f"      Localizacao: {veiculo.localizacao}")
        print(f"      Autonomia: {veiculo.autonomia_atual:.1f}/{veiculo.autonomia_maxima:.1f} km")
        print(f"      Estado: {veiculo.estado.value}")
    
    print("\n" + "=" * 70)
    print(" DEMONSTRACAO COMPLETA ".center(70, '='))
    print("=" * 70 + "\n")
    
    return 0


if __name__ == '__main__':
    exit(main())

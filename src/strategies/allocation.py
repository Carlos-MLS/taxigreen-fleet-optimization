"""
Estrategias de Alocacao de Veiculos a Pedidos.

Este modulo implementa diferentes estrategias para decidir qual veiculo
deve atender cada pedido de transporte. Cada estrategia otimiza um
criterio diferente, permitindo flexibilidade na gestao da frota.

Estrategias implementadas:
    - NearestVehicleStrategy: Minimiza distancia ate ao cliente (tempo de resposta)
    - LowestCostStrategy: Minimiza custo operacional total (euros)
    - EcoFriendlyStrategy: Prioriza veiculos eletricos (emissoes CO2)

O padrao Strategy permite adicionar novas estrategias sem modificar
o codigo existente (principio Open-Closed).

Autores: Grupo 18 - Inteligencia Artificial 2024/2025
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict
import math

from ..models.vehicle import Vehicle, VehicleState, VehicleType
from ..models.request import Request
from ..models.city import City


class AllocationStrategy(ABC):
    """
    Classe base abstrata para estrategias de alocacao.
    
    Define a interface comum que todas as estrategias devem implementar.
    Usa o padrao Template Method para reutilizar logica comum
    (verificacoes de disponibilidade, calculo de distancias).
    """
    
    def __init__(self, cidade: City):
        """
        Inicializa a estrategia com o grafo da cidade.
        
        O grafo da cidade e necessario para calcular distancias
        entre localizacoes (veiculos, origens, destinos).
        
        Args:
            cidade: Objeto City com o grafo de localizacoes e arestas
        """
        self.cidade = cidade
    
    @abstractmethod
    def alocar_veiculo(
        self,
        pedido: Request,
        frota: Dict[str, Vehicle]
    ) -> Optional[Vehicle]:
        """
        Metodo abstrato que seleciona o melhor veiculo para um pedido.
        
        Cada estrategia concreta implementa a sua propria logica
        de selecao baseada em diferentes criterios.
        
        Args:
            pedido: O pedido de transporte a atender
            frota: Dicionario {id: Vehicle} com todos os veiculos
            
        Returns:
            O veiculo selecionado, ou None se nenhum for viavel
        """
        pass
    
    def _calcular_distancia(self, origem: str, destino: str) -> float:
        """
        Calcula a distancia entre dois nos do grafo.
        
        Tenta primeiro usar a aresta direta (se existir).
        Se nao existir, calcula a distancia euclidiana.
        
        Args:
            origem: ID do no de origem
            destino: ID do no de destino
            
        Returns:
            Distancia em km (ou 999 se nao for possivel calcular)
        """
        # Caso trivial: mesma localizacao
        if origem == destino:
            return 0.0
        
        # Tentar obter aresta direta do grafo
        aresta = self.cidade.obter_aresta(origem, destino)
        if aresta:
            return aresta.distancia
        
        # Fallback: calcular distancia euclidiana se tivermos coordenadas
        if hasattr(self.cidade, 'coordenadas'):
            coords = self.cidade.coordenadas
            if origem in coords and destino in coords:
                x1, y1 = coords[origem]
                x2, y2 = coords[destino]
                return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        
        # Se nao conseguirmos calcular, retornar valor alto
        # (efetivamente descarta esta opcao)
        return 999.0
    
    def _pode_atender(self, veiculo: Vehicle, pedido: Request) -> bool:
        """
        Verifica se um veiculo pode atender um pedido.
        
        Sao verificadas tres condicoes:
        1. O veiculo esta disponivel (nao ocupado nem em manutencao)
        2. O veiculo tem capacidade para os passageiros
        3. O veiculo tem autonomia suficiente (com margem de 20%)
        
        Args:
            veiculo: O veiculo a verificar
            pedido: O pedido a atender
            
        Returns:
            True se o veiculo pode atender o pedido, False caso contrario
        """
        # Verificar disponibilidade
        if veiculo.estado != VehicleState.AVAILABLE:
            return False
        
        # Verificar capacidade de passageiros
        if veiculo.capacidade < pedido.num_passageiros:
            return False
        
        # Calcular distancia total da viagem
        dist_pickup = self._calcular_distancia(veiculo.localizacao, pedido.origem)
        dist_trip = self._calcular_distancia(pedido.origem, pedido.destino)
        
        # Verificar autonomia com margem de seguranca de 20%
        # A margem evita que o veiculo fique sem bateria/combustivel
        if veiculo.autonomia_atual < (dist_pickup + dist_trip) * 1.2:
            return False
        
        return True


class NearestVehicleStrategy(AllocationStrategy):
    """
    Estrategia que seleciona o veiculo mais proximo do cliente.
    
    Prioriza a rapidez de resposta, escolhendo sempre o veiculo
    que esta mais perto do ponto de recolha, independentemente
    do tipo ou custo. Ideal para situacoes onde o tempo de
    espera do cliente e o fator mais importante.
    """
    
    def alocar_veiculo(
        self,
        pedido: Request,
        frota: Dict[str, Vehicle]
    ) -> Optional[Vehicle]:
        """
        Seleciona o veiculo mais proximo da origem do pedido.
        
        Itera sobre todos os veiculos, calcula a distancia de cada um
        ate ao ponto de recolha, e devolve o mais proximo.
        """
        melhor_veiculo = None
        menor_distancia = float('inf')
        
        for veiculo in frota.values():
            if not self._pode_atender(veiculo, pedido):
                continue
            
            dist = self._calcular_distancia(veiculo.localizacao, pedido.origem)
            
            if dist < menor_distancia:
                menor_distancia = dist
                melhor_veiculo = veiculo
        
        return melhor_veiculo


class LowestCostStrategy(AllocationStrategy):
    """
    Estrategia que minimiza o custo operacional da viagem.
    
    Calcula o custo total (pickup + transporte) * custo_por_km
    para cada veiculo e escolhe o mais economico. Como os veiculos
    eletricos tem custo inferior (0.12 vs 0.25 EUR/km), esta
    estrategia tende a favorece-los quando disponiveis.
    """
    
    def alocar_veiculo(
        self,
        pedido: Request,
        frota: Dict[str, Vehicle]
    ) -> Optional[Vehicle]:
        """
        Seleciona o veiculo com menor custo operacional total.
        
        Calcula o custo da viagem completa (pickup + transporte)
        para cada veiculo disponivel e escolhe o mais barato.
        """
        melhor_veiculo = None
        menor_custo = float('inf')
        
        for veiculo in frota.values():
            # Verificar se o veiculo pode atender o pedido
            if not self._pode_atender(veiculo, pedido):
                continue
            
            # Calcular distancias
            dist_pickup = self._calcular_distancia(veiculo.localizacao, pedido.origem)
            dist_trip = self._calcular_distancia(pedido.origem, pedido.destino)
            
            # Custo = distancia total * custo por km do veiculo
            custo = (dist_pickup + dist_trip) * veiculo.custo_km
            
            # Manter o melhor (menor custo)
            if custo < menor_custo:
                menor_custo = custo
                melhor_veiculo = veiculo
        
        return melhor_veiculo


class EcoFriendlyStrategy(AllocationStrategy):
    """
    Estrategia que prioriza veiculos eletricos para minimizar emissoes.
    
    Tenta sempre usar um veiculo eletrico (escolhendo o mais proximo),
    e so recorre a combustao se nenhum eletrico tiver disponibilidade
    ou autonomia. Alinha-se com objetivos de sustentabilidade e
    e util para clientes com preferencias ambientais.
    """
    
    def alocar_veiculo(
        self,
        pedido: Request,
        frota: Dict[str, Vehicle]
    ) -> Optional[Vehicle]:
        """
        Seleciona veiculo priorizando opcoes eletricas.
        
        Separa os veiculos viaveis em eletricos e combustao,
        e so usa combustao se nao houver eletricos disponiveis.
        """
        # Listas para separar veiculos por tipo
        veiculos_eletricos = []
        veiculos_combustao = []
        
        # Classificar veiculos viaveis por tipo
        for veiculo in frota.values():
            if not self._pode_atender(veiculo, pedido):
                continue
            
            # Calcular distancia ao cliente
            dist = self._calcular_distancia(veiculo.localizacao, pedido.origem)
            
            # Separar por tipo de veiculo
            if veiculo.tipo == VehicleType.ELECTRIC:
                veiculos_eletricos.append((dist, veiculo))
            else:
                veiculos_combustao.append((dist, veiculo))
        
        # Prioridade 1: usar veiculo eletrico se disponivel
        # Ordenar por distancia e escolher o mais proximo
        if veiculos_eletricos:
            veiculos_eletricos.sort(key=lambda x: x[0])  # Ordenar por distancia
            return veiculos_eletricos[0][1]  # Devolver o veiculo (nao a distancia)
        
        # Prioridade 2: usar veiculo a combustao como fallback
        # So chegamos aqui se nao houver eletricos viaveis
        if veiculos_combustao:
            veiculos_combustao.sort(key=lambda x: x[0])
            return veiculos_combustao[0][1]
        
        return None


def criar_estrategia(nome: str, cidade: City, **kwargs) -> AllocationStrategy:
    """
    Factory para criar estrategias.
    
    Args:
        nome: Nome da estrategia ('nearest', 'lowest_cost', 'eco_friendly')
        cidade: Grafo da cidade
        **kwargs: Parametros adicionais para estrategia
        
    Returns:
        Instancia da estrategia
    """
    estrategias = {
        'nearest': NearestVehicleStrategy,
        'lowest_cost': LowestCostStrategy,
        'eco_friendly': EcoFriendlyStrategy
    }
    
    if nome not in estrategias:
        raise ValueError(f"Estrategia '{nome}' nao encontrada. Opcoes: {list(estrategias.keys())}")
    
    return estrategias[nome](cidade, **kwargs)

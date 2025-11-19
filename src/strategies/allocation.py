"""
Estratégias de alocação de veículos a pedidos.
Implementa diferentes abordagens de decisão.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict
import math

from ..models.vehicle import Vehicle, VehicleState, VehicleType
from ..models.request import Request
from ..models.city import City


class AllocationStrategy(ABC):
    """Estratégia base de alocação."""
    
    def __init__(self, cidade: City):
        """
        Inicializa estratégia.
        
        Args:
            cidade: Grafo da cidade
        """
        self.cidade = cidade
    
    @abstractmethod
    def alocar_veiculo(
        self,
        pedido: Request,
        frota: Dict[str, Vehicle]
    ) -> Optional[Vehicle]:
        """
        Aloca melhor veículo para pedido.
        
        Args:
            pedido: Pedido a atender
            frota: Dicionário de veículos disponíveis
            
        Returns:
            Veículo selecionado ou None
        """
        pass
    
    def _calcular_distancia(self, origem: str, destino: str) -> float:
        """Calcula distância entre dois nós."""
        if origem == destino:
            return 0.0
        
        aresta = self.cidade.obter_aresta(origem, destino)
        if aresta:
            return aresta.distancia
        
        # Usar coordenadas
        if hasattr(self.cidade, 'coordenadas'):
            coords = self.cidade.coordenadas
            if origem in coords and destino in coords:
                x1, y1 = coords[origem]
                x2, y2 = coords[destino]
                return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        
        return 999.0
    
    def _pode_atender(self, veiculo: Vehicle, pedido: Request) -> bool:
        """Verifica se veículo pode atender pedido."""
        # Deve estar disponível
        if veiculo.estado != VehicleState.AVAILABLE:
            return False
        
        # Capacidade suficiente
        if veiculo.capacidade < pedido.num_passageiros:
            return False
        
        # Autonomia suficiente
        dist_pickup = self._calcular_distancia(veiculo.localizacao, pedido.origem)
        dist_trip = self._calcular_distancia(pedido.origem, pedido.destino)
        
        if veiculo.autonomia_atual < (dist_pickup + dist_trip) * 1.2:
            return False
        
        return True


class NearestVehicleStrategy(AllocationStrategy):
    """
    Estratégia: Veículo Mais Próximo.
    
    Aloca o veículo disponível mais próximo do cliente.
    Simples e rápida, mas pode não ser ótima.
    """
    
    def alocar_veiculo(
        self,
        pedido: Request,
        frota: Dict[str, Vehicle]
    ) -> Optional[Vehicle]:
        """Aloca veículo mais próximo."""
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
    Estratégia: Menor Custo Operacional.
    
    Aloca veículo que minimiza custo operacional total.
    Considera custo por km do veículo.
    """
    
    def alocar_veiculo(
        self,
        pedido: Request,
        frota: Dict[str, Vehicle]
    ) -> Optional[Vehicle]:
        """Aloca veículo com menor custo."""
        melhor_veiculo = None
        menor_custo = float('inf')
        
        for veiculo in frota.values():
            if not self._pode_atender(veiculo, pedido):
                continue
            
            # Calcular custo total
            dist_pickup = self._calcular_distancia(veiculo.localizacao, pedido.origem)
            dist_trip = self._calcular_distancia(pedido.origem, pedido.destino)
            
            custo = (dist_pickup + dist_trip) * veiculo.custo_km
            
            if custo < menor_custo:
                menor_custo = custo
                melhor_veiculo = veiculo
        
        return melhor_veiculo


class EcoFriendlyStrategy(AllocationStrategy):
    """
    Estratégia: Ecológica.
    
    Prioriza veículos elétricos quando possível.
    Minimiza emissões de CO2.
    """
    
    def alocar_veiculo(
        self,
        pedido: Request,
        frota: Dict[str, Vehicle]
    ) -> Optional[Vehicle]:
        """Aloca veículo priorizando elétricos."""
        # Tentar veículos elétricos primeiro
        veiculos_eletricos = []
        veiculos_combustao = []
        
        for veiculo in frota.values():
            if not self._pode_atender(veiculo, pedido):
                continue
            
            if veiculo.tipo == VehicleType.ELECTRIC:
                dist = self._calcular_distancia(veiculo.localizacao, pedido.origem)
                veiculos_eletricos.append((dist, veiculo))
            else:
                dist = self._calcular_distancia(veiculo.localizacao, pedido.origem)
                veiculos_combustao.append((dist, veiculo))
        
        # Preferir elétrico mais próximo
        if veiculos_eletricos:
            veiculos_eletricos.sort(key=lambda x: x[0])
            return veiculos_eletricos[0][1]
        
        # Senão, combustão mais próximo
        if veiculos_combustao:
            veiculos_combustao.sort(key=lambda x: x[0])
            return veiculos_combustao[0][1]
        
        return None


class MinEmissionsStrategy(AllocationStrategy):
    """
    Estratégia: Mínimas Emissões.
    
    Aloca veículo que minimiza emissões totais de CO2.
    """
    
    def alocar_veiculo(
        self,
        pedido: Request,
        frota: Dict[str, Vehicle]
    ) -> Optional[Vehicle]:
        """Aloca veículo com menores emissões."""
        melhor_veiculo = None
        menores_emissoes = float('inf')
        
        for veiculo in frota.values():
            if not self._pode_atender(veiculo, pedido):
                continue
            
            # Calcular emissões totais
            dist_pickup = self._calcular_distancia(veiculo.localizacao, pedido.origem)
            dist_trip = self._calcular_distancia(pedido.origem, pedido.destino)
            dist_total = dist_pickup + dist_trip
            
            emissoes = veiculo.calcular_emissoes(dist_total)
            
            if emissoes < menores_emissoes:
                menores_emissoes = emissoes
                melhor_veiculo = veiculo
        
        return melhor_veiculo


class BalancedStrategy(AllocationStrategy):
    """
    Estratégia: Balanceada.
    
    Combina múltiplos critérios com pesos:
    - Distância (30%)
    - Custo (30%)
    - Emissões (20%)
    - Autonomia restante (20%)
    """
    
    def __init__(
        self,
        cidade: City,
        peso_distancia: float = 0.30,
        peso_custo: float = 0.30,
        peso_emissoes: float = 0.20,
        peso_autonomia: float = 0.20
    ):
        super().__init__(cidade)
        self.peso_distancia = peso_distancia
        self.peso_custo = peso_custo
        self.peso_emissoes = peso_emissoes
        self.peso_autonomia = peso_autonomia
    
    def alocar_veiculo(
        self,
        pedido: Request,
        frota: Dict[str, Vehicle]
    ) -> Optional[Vehicle]:
        """Aloca veículo com melhor score balanceado."""
        candidatos = []
        
        for veiculo in frota.values():
            if not self._pode_atender(veiculo, pedido):
                continue
            
            # Calcular métricas
            dist_pickup = self._calcular_distancia(veiculo.localizacao, pedido.origem)
            dist_trip = self._calcular_distancia(pedido.origem, pedido.destino)
            dist_total = dist_pickup + dist_trip
            
            custo = dist_total * veiculo.custo_km
            emissoes = veiculo.calcular_emissoes(dist_total)
            autonomia_ratio = veiculo.autonomia_atual / veiculo.autonomia_maxima
            
            candidatos.append((dist_total, custo, emissoes, autonomia_ratio, veiculo))
        
        if not candidatos:
            return None
        
        # Normalizar valores (0-1)
        max_dist = max(c[0] for c in candidatos)
        max_custo = max(c[1] for c in candidatos)
        max_emissoes = max(c[2] for c in candidatos) if max(c[2] for c in candidatos) > 0 else 1.0
        
        # Calcular scores
        scores = []
        for dist, custo, emissoes, autonomia, veiculo in candidatos:
            score = (
                self.peso_distancia * (dist / max_dist if max_dist > 0 else 0) +
                self.peso_custo * (custo / max_custo if max_custo > 0 else 0) +
                self.peso_emissoes * (emissoes / max_emissoes) +
                self.peso_autonomia * (1.0 - autonomia)  # Penaliza baixa autonomia
            )
            scores.append((score, veiculo))
        
        # Retornar com menor score (melhor)
        scores.sort(key=lambda x: x[0])
        return scores[0][1]


class PriorityAwareStrategy(AllocationStrategy):
    """
    Estratégia: Consciente de Prioridade.
    
    Considera prioridade do pedido na alocação:
    - Urgente/Premium: veículo mais próximo
    - Normal: balanceado custo/distância
    """
    
    def alocar_veiculo(
        self,
        pedido: Request,
        frota: Dict[str, Vehicle]
    ) -> Optional[Vehicle]:
        """Aloca considerando prioridade."""
        from ..models.request import Priority
        
        # Para urgentes e premium, priorizar velocidade (mais próximo)
        if pedido.prioridade in [Priority.URGENT, Priority.PREMIUM]:
            estrategia = NearestVehicleStrategy(self.cidade)
            return estrategia.alocar_veiculo(pedido, frota)
        
        # Para normais, usar estratégia balanceada
        estrategia = BalancedStrategy(self.cidade)
        return estrategia.alocar_veiculo(pedido, frota)


def criar_estrategia(nome: str, cidade: City, **kwargs) -> AllocationStrategy:
    """
    Factory para criar estratégias.
    
    Args:
        nome: Nome da estratégia ('nearest', 'lowest_cost', 'eco', 'balanced', 'priority')
        cidade: Grafo da cidade
        **kwargs: Parâmetros adicionais para estratégia
        
    Returns:
        Instância da estratégia
    """
    estrategias = {
        'nearest': NearestVehicleStrategy,
        'lowest_cost': LowestCostStrategy,
        'eco': EcoFriendlyStrategy,
        'eco_friendly': EcoFriendlyStrategy,
        'min_emissions': MinEmissionsStrategy,
        'balanced': BalancedStrategy,
        'priority': PriorityAwareStrategy
    }
    
    if nome not in estrategias:
        raise ValueError(f"Estratégia '{nome}' não encontrada. Opções: {list(estrategias.keys())}")
    
    return estrategias[nome](cidade, **kwargs)

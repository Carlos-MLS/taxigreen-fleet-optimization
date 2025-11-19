"""
Módulo que define a classe Vehicle (Veículo).
Representa veículos da frota (elétricos e a combustão).
"""

from enum import Enum
from typing import Optional, Tuple


class VehicleType(Enum):
    """Tipos de veículos disponíveis."""
    ELECTRIC = "elétrico"
    COMBUSTION = "combustão"


class VehicleState(Enum):
    """Estados possíveis de um veículo."""
    AVAILABLE = "disponível"
    OCCUPIED = "ocupado"
    CHARGING = "em_recarga"
    TRAVELING = "em_deslocacao"


class Vehicle:
    """
    Representa um veículo da frota TaxiGreen.
    
    Attributes:
        id: Identificador único do veículo
        tipo: Tipo de motorização (elétrico/combustão)
        localizacao: Nó atual no grafo da cidade
        autonomia_atual: Km restantes
        autonomia_maxima: Capacidade máxima em km
        capacidade: Número máximo de passageiros
        custo_km: Custo operacional por quilómetro (€)
        estado: Estado atual do veículo
        passageiros_atuais: Número de passageiros a bordo
        destino_atual: Destino do trajeto atual (se aplicável)
    """
    
    def __init__(
        self,
        vehicle_id: str,
        tipo: VehicleType,
        localizacao: str,
        autonomia_maxima: float,
        capacidade: int,
        custo_km: float
    ):
        """
        Inicializa um veículo.
        
        Args:
            vehicle_id: Identificador único
            tipo: Tipo de veículo (ELECTRIC ou COMBUSTION)
            localizacao: Localização inicial (nó)
            autonomia_maxima: Autonomia máxima em km
            capacidade: Capacidade máxima de passageiros
            custo_km: Custo operacional por km
        """
        self.id = vehicle_id
        self.tipo = tipo
        self.localizacao = localizacao
        self.autonomia_atual = autonomia_maxima  # Inicia com tanque/bateria cheio
        self.autonomia_maxima = autonomia_maxima
        self.capacidade = capacidade
        self.custo_km = custo_km
        self.estado = VehicleState.AVAILABLE
        self.passageiros_atuais = 0
        self.destino_atual: Optional[str] = None
        
        # Métricas de operação
        self.km_percorridos = 0.0
        self.km_com_passageiros = 0.0
        self.km_vazios = 0.0
        self.num_viagens = 0
        self.tempo_ocupado = 0.0
        self.tempo_total = 0.0
    
    def pode_aceitar_pedido(self, num_passageiros: int, distancia_total: float) -> bool:
        """
        Verifica se o veículo pode aceitar um pedido.
        
        Args:
            num_passageiros: Número de passageiros do pedido
            distancia_total: Distância total estimada (recolha + viagem)
            
        Returns:
            True se pode aceitar, False caso contrário
        """
        tem_capacidade = (self.passageiros_atuais + num_passageiros) <= self.capacidade
        tem_autonomia = self.autonomia_atual >= distancia_total
        esta_disponivel = self.estado == VehicleState.AVAILABLE
        
        return tem_capacidade and tem_autonomia and esta_disponivel
    
    def consumir_autonomia(self, distancia: float, com_passageiros: bool = False):
        """
        Consome autonomia ao viajar uma distância.
        
        Args:
            distancia: Distância percorrida em km
            com_passageiros: Se a viagem foi com passageiros
        """
        # Fator de consumo (pode ser ajustado)
        fator_consumo = 1.0
        
        # Veículos elétricos consomem mais em certas condições
        if self.tipo == VehicleType.ELECTRIC:
            # Consumo base: ~15-20 kWh/100km (simplificado para km)
            fator_consumo = 1.1 if com_passageiros else 1.0
        
        consumo = distancia * fator_consumo
        self.autonomia_atual = max(0, self.autonomia_atual - consumo)
        
        # Atualizar métricas
        self.km_percorridos += distancia
        if com_passageiros:
            self.km_com_passageiros += distancia
        else:
            self.km_vazios += distancia
    
    def recarregar(self):
        """Recarrega/reabastece o veículo completamente."""
        self.autonomia_atual = self.autonomia_maxima
    
    def precisa_recarga(self, limiar: float = 0.2) -> bool:
        """
        Verifica se o veículo precisa de recarga urgente.
        
        Args:
            limiar: Percentagem mínima de autonomia (default: 20%)
            
        Returns:
            True se autonomia < limiar
        """
        percentagem_autonomia = self.autonomia_atual / self.autonomia_maxima
        return percentagem_autonomia < limiar
    
    def tempo_recarga_estimado(self) -> float:
        """
        Estima o tempo necessário para recarga completa.
        
        Returns:
            Tempo em minutos
        """
        if self.tipo == VehicleType.ELECTRIC:
            # Elétricos: 30-60 min (dependendo da carga restante)
            percentagem_vazio = 1 - (self.autonomia_atual / self.autonomia_maxima)
            return 30 + (percentagem_vazio * 30)  # 30-60 min
        else:
            # Combustão: 5-10 min
            return 7.5  # Média
    
    def calcular_emissoes(self, distancia: float) -> float:
        """
        Calcula emissões de CO2 para uma distância.
        
        Args:
            distancia: Distância em km
            
        Returns:
            Emissões em kg de CO2
        """
        if self.tipo == VehicleType.ELECTRIC:
            return 0.0  # Sem emissões locais
        else:
            # Combustão: ~150 g CO2/km média
            emissoes_por_km = 0.150  # kg CO2/km
            return distancia * emissoes_por_km
    
    def taxa_ocupacao(self) -> float:
        """
        Calcula a taxa de ocupação do veículo.
        
        Returns:
            Percentagem de tempo ocupado (0-1)
        """
        if self.tempo_total == 0:
            return 0.0
        return self.tempo_ocupado / self.tempo_total
    
    def __str__(self) -> str:
        """Representação string do veículo."""
        return (
            f"Veículo {self.id} ({self.tipo.value}): "
            f"Local={self.localizacao}, "
            f"Autonomia={self.autonomia_atual:.1f}/{self.autonomia_maxima:.1f}km, "
            f"Estado={self.estado.value}, "
            f"Passageiros={self.passageiros_atuais}/{self.capacidade}"
        )
    
    def __repr__(self) -> str:
        """Representação para debug."""
        return f"Vehicle(id={self.id}, tipo={self.tipo.value}, loc={self.localizacao})"
    
    def to_dict(self) -> dict:
        """
        Converte o veículo para dicionário (útil para serialização).
        
        Returns:
            Dicionário com todos os atributos
        """
        return {
            'id': self.id,
            'tipo': self.tipo.value,
            'localizacao': self.localizacao,
            'autonomia_atual': self.autonomia_atual,
            'autonomia_maxima': self.autonomia_maxima,
            'capacidade': self.capacidade,
            'custo_km': self.custo_km,
            'estado': self.estado.value,
            'passageiros_atuais': self.passageiros_atuais,
            'destino_atual': self.destino_atual,
            'metricas': {
                'km_percorridos': self.km_percorridos,
                'km_com_passageiros': self.km_com_passageiros,
                'km_vazios': self.km_vazios,
                'num_viagens': self.num_viagens,
                'taxa_ocupacao': self.taxa_ocupacao()
            }
        }

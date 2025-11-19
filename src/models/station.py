"""
Módulo que define a classe Station (Estação de Recarga/Abastecimento).
Representa estações onde veículos podem reabastecer.
"""

from enum import Enum
from typing import Optional


class StationType(Enum):
    """Tipos de estações disponíveis."""
    ELECTRIC_CHARGING = "recarga_eletrica"
    FUEL_STATION = "posto_combustivel"


class StationStatus(Enum):
    """Estados possíveis de uma estação."""
    AVAILABLE = "disponível"
    OCCUPIED = "ocupado"
    BROKEN = "avariado"


class Station:
    """
    Representa uma estação de recarga ou abastecimento.
    
    Attributes:
        id: Identificador único da estação
        tipo: Tipo de estação (elétrica/combustível)
        localizacao: Nó no grafo onde está situada
        disponibilidade: Estado atual da estação
        tempo_servico: Tempo médio de atendimento (minutos)
        capacidade: Número de veículos que podem ser atendidos simultaneamente
        veiculos_em_servico: Conjunto de IDs de veículos sendo atendidos
    """
    
    def __init__(
        self,
        station_id: str,
        tipo: StationType,
        localizacao: str,
        tempo_servico: float,
        capacidade: int = 1
    ):
        """
        Inicializa uma estação.
        
        Args:
            station_id: Identificador único
            tipo: Tipo de estação
            localizacao: Nó no grafo
            tempo_servico: Tempo médio de atendimento em minutos
            capacidade: Número de posições de atendimento
        """
        self.id = station_id
        self.tipo = tipo
        self.localizacao = localizacao
        self.tempo_servico = tempo_servico
        self.capacidade = capacidade
        self.disponibilidade = StationStatus.AVAILABLE
        self.veiculos_em_servico: set = set()
        
        # Métricas
        self.total_atendimentos = 0
        self.tempo_total_uso = 0.0
    
    def esta_disponivel(self) -> bool:
        """
        Verifica se a estação está disponível para uso.
        
        Returns:
            True se disponível e com capacidade
        """
        tem_capacidade = len(self.veiculos_em_servico) < self.capacidade
        nao_avariada = self.disponibilidade != StationStatus.BROKEN
        return tem_capacidade and nao_avariada
    
    def aceitar_veiculo(self, veiculo_id: str) -> bool:
        """
        Tenta aceitar um veículo para serviço.
        
        Args:
            veiculo_id: ID do veículo
            
        Returns:
            True se aceite, False se não há capacidade
        """
        if not self.esta_disponivel():
            return False
        
        self.veiculos_em_servico.add(veiculo_id)
        
        # Atualizar disponibilidade
        if len(self.veiculos_em_servico) >= self.capacidade:
            self.disponibilidade = StationStatus.OCCUPIED
        
        return True
    
    def libertar_veiculo(self, veiculo_id: str):
        """
        Liberta um veículo após serviço completo.
        
        Args:
            veiculo_id: ID do veículo
        """
        if veiculo_id in self.veiculos_em_servico:
            self.veiculos_em_servico.remove(veiculo_id)
            self.total_atendimentos += 1
            self.tempo_total_uso += self.tempo_servico
        
        # Atualizar disponibilidade
        if self.disponibilidade != StationStatus.BROKEN:
            if len(self.veiculos_em_servico) < self.capacidade:
                self.disponibilidade = StationStatus.AVAILABLE
    
    def avariar(self):
        """Marca a estação como avariada."""
        self.disponibilidade = StationStatus.BROKEN
    
    def reparar(self):
        """Repara a estação, tornando-a disponível."""
        if len(self.veiculos_em_servico) < self.capacidade:
            self.disponibilidade = StationStatus.AVAILABLE
        else:
            self.disponibilidade = StationStatus.OCCUPIED
    
    def taxa_utilizacao(self, tempo_total_simulacao: float) -> float:
        """
        Calcula a taxa de utilização da estação.
        
        Args:
            tempo_total_simulacao: Tempo total da simulação
            
        Returns:
            Percentagem de utilização (0-1)
        """
        if tempo_total_simulacao == 0:
            return 0.0
        return self.tempo_total_uso / tempo_total_simulacao
    
    def __str__(self) -> str:
        """Representação string da estação."""
        return (
            f"Estação {self.id} ({self.tipo.value}): "
            f"Local={self.localizacao}, "
            f"Status={self.disponibilidade.value}, "
            f"Em uso={len(self.veiculos_em_servico)}/{self.capacidade}"
        )
    
    def __repr__(self) -> str:
        """Representação para debug."""
        return f"Station(id={self.id}, tipo={self.tipo.value}, loc={self.localizacao})"
    
    def to_dict(self) -> dict:
        """
        Converte a estação para dicionário.
        
        Returns:
            Dicionário com todos os atributos
        """
        return {
            'id': self.id,
            'tipo': self.tipo.value,
            'localizacao': self.localizacao,
            'tempo_servico': self.tempo_servico,
            'capacidade': self.capacidade,
            'disponibilidade': self.disponibilidade.value,
            'veiculos_em_servico': list(self.veiculos_em_servico),
            'metricas': {
                'total_atendimentos': self.total_atendimentos,
                'tempo_total_uso': self.tempo_total_uso
            }
        }

"""
Módulo que define a classe Request (Pedido de Transporte).
Representa pedidos de clientes que chegam dinamicamente.
"""

from enum import Enum
from typing import Optional
from datetime import datetime


class Priority(Enum):
    """Níveis de prioridade de pedidos."""
    NORMAL = "normal"
    URGENT = "urgente"
    PREMIUM = "premium"


class EnvironmentalPreference(Enum):
    """Preferência ambiental do cliente."""
    YES = "sim"
    NO = "não"
    INDIFFERENT = "indiferente"


class RequestStatus(Enum):
    """Estados possíveis de um pedido."""
    PENDING = "pendente"
    ASSIGNED = "atribuído"
    IN_PROGRESS = "em_progresso"
    COMPLETED = "concluído"
    REJECTED = "rejeitado"


class Request:
    """
    Representa um pedido de transporte.
    
    Attributes:
        id: Identificador único do pedido
        origem: Localização de recolha (nó)
        destino: Localização de entrega (nó)
        num_passageiros: Número de passageiros
        horario_pedido: Timestamp da criação
        prioridade: Nível de prioridade
        preferencia_ambiental: Preferência por veículo elétrico
        tempo_espera_max: Tempo máximo aceitável de espera (minutos)
        status: Estado atual do pedido
        veiculo_atribuido: ID do veículo atribuído (se houver)
    """
    
    def __init__(
        self,
        request_id: str,
        origem: str,
        destino: str,
        num_passageiros: int,
        horario_pedido: float,
        prioridade: Priority = Priority.NORMAL,
        preferencia_ambiental: EnvironmentalPreference = EnvironmentalPreference.INDIFFERENT,
        tempo_espera_max: float = 15.0  # 15 minutos por defeito
    ):
        """
        Inicializa um pedido de transporte.
        
        Args:
            request_id: Identificador único
            origem: Nó de origem
            destino: Nó de destino
            num_passageiros: Número de passageiros (1-4 tipicamente)
            horario_pedido: Timestamp da criação
            prioridade: Prioridade do pedido
            preferencia_ambiental: Preferência por veículo elétrico
            tempo_espera_max: Tempo máximo de espera em minutos
        """
        self.id = request_id
        self.origem = origem
        self.destino = destino
        self.num_passageiros = num_passageiros
        self.horario_pedido = horario_pedido
        self.prioridade = prioridade
        self.preferencia_ambiental = preferencia_ambiental
        self.tempo_espera_max = tempo_espera_max
        
        # Estado e tracking
        self.status = RequestStatus.PENDING
        self.veiculo_atribuido: Optional[str] = None
        self.tempo_atribuicao: Optional[float] = None
        self.tempo_recolha: Optional[float] = None
        self.tempo_entrega: Optional[float] = None
        self.motivo_rejeicao: Optional[str] = None
    
    def atribuir_veiculo(self, veiculo_id: str, tempo_atual: float):
        """
        Atribui um veículo ao pedido.
        
        Args:
            veiculo_id: ID do veículo atribuído
            tempo_atual: Timestamp atual
        """
        self.veiculo_atribuido = veiculo_id
        self.tempo_atribuicao = tempo_atual
        self.status = RequestStatus.ASSIGNED
    
    def iniciar_viagem(self, tempo_atual: float):
        """
        Marca o início da viagem (passageiros recolhidos).
        
        Args:
            tempo_atual: Timestamp atual
        """
        self.tempo_recolha = tempo_atual
        self.status = RequestStatus.IN_PROGRESS
    
    def completar(self, tempo_atual: float):
        """
        Marca o pedido como completo.
        
        Args:
            tempo_atual: Timestamp atual
        """
        self.tempo_entrega = tempo_atual
        self.status = RequestStatus.COMPLETED
    
    def rejeitar(self, motivo: str):
        """
        Rejeita o pedido.
        
        Args:
            motivo: Razão da rejeição
        """
        self.status = RequestStatus.REJECTED
        self.motivo_rejeicao = motivo
    
    def tempo_espera_atual(self, tempo_atual: float) -> float:
        """
        Calcula o tempo de espera atual desde a criação.
        
        Args:
            tempo_atual: Timestamp atual
            
        Returns:
            Tempo de espera em minutos
        """
        return tempo_atual - self.horario_pedido
    
    def tempo_resposta(self) -> Optional[float]:
        """
        Calcula o tempo de resposta (criação até atribuição).
        
        Returns:
            Tempo em minutos, ou None se não atribuído
        """
        if self.tempo_atribuicao is None:
            return None
        return self.tempo_atribuicao - self.horario_pedido
    
    def tempo_total_servico(self) -> Optional[float]:
        """
        Calcula o tempo total de serviço (criação até entrega).
        
        Returns:
            Tempo em minutos, ou None se não completo
        """
        if self.tempo_entrega is None:
            return None
        return self.tempo_entrega - self.horario_pedido
    
    def excedeu_tempo_espera(self, tempo_atual: float) -> bool:
        """
        Verifica se o tempo máximo de espera foi excedido.
        
        Args:
            tempo_atual: Timestamp atual
            
        Returns:
            True se excedeu, False caso contrário
        """
        tempo_espera = self.tempo_espera_atual(tempo_atual)
        return tempo_espera > self.tempo_espera_max
    
    def peso_prioridade(self) -> float:
        """
        Retorna o peso numérico da prioridade.
        
        Returns:
            Peso para cálculo de custos
        """
        pesos = {
            Priority.NORMAL: 1.0,
            Priority.URGENT: 2.0,
            Priority.PREMIUM: 3.0
        }
        return pesos[self.prioridade]
    
    def prefere_eletrico(self) -> bool:
        """
        Verifica se o cliente prefere veículo elétrico.
        
        Returns:
            True se prefere elétrico
        """
        return self.preferencia_ambiental == EnvironmentalPreference.YES
    
    def __str__(self) -> str:
        """Representação string do pedido."""
        return (
            f"Pedido {self.id}: "
            f"{self.origem}→{self.destino}, "
            f"{self.num_passageiros} pass., "
            f"Prioridade={self.prioridade.value}, "
            f"Status={self.status.value}"
        )
    
    def __repr__(self) -> str:
        """Representação para debug."""
        return f"Request(id={self.id}, {self.origem}→{self.destino}, status={self.status.value})"
    
    def to_dict(self) -> dict:
        """
        Converte o pedido para dicionário.
        
        Returns:
            Dicionário com todos os atributos
        """
        return {
            'id': self.id,
            'origem': self.origem,
            'destino': self.destino,
            'num_passageiros': self.num_passageiros,
            'horario_pedido': self.horario_pedido,
            'prioridade': self.prioridade.value,
            'preferencia_ambiental': self.preferencia_ambiental.value,
            'tempo_espera_max': self.tempo_espera_max,
            'status': self.status.value,
            'veiculo_atribuido': self.veiculo_atribuido,
            'tempos': {
                'atribuicao': self.tempo_atribuicao,
                'recolha': self.tempo_recolha,
                'entrega': self.tempo_entrega,
                'resposta': self.tempo_resposta(),
                'total_servico': self.tempo_total_servico()
            },
            'motivo_rejeicao': self.motivo_rejeicao
        }

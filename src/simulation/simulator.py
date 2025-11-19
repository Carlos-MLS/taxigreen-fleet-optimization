"""
Simulador de operação da frota de táxis.
Processa eventos dinâmicos ao longo do tempo.
"""

from typing import List, Dict, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import random
from copy import deepcopy

from ..models.vehicle import Vehicle, VehicleState, VehicleType
from ..models.request import Request, Priority, EnvironmentalPreference
from ..models.city import City
from ..models.station import Station
from .metrics import MetricsCollector


class EventType(Enum):
    """Tipos de eventos na simulação."""
    NOVO_PEDIDO = "novo_pedido"
    VEICULO_CHEGOU_CLIENTE = "veiculo_chegou_cliente"
    VEICULO_CHEGOU_DESTINO = "veiculo_chegou_destino"
    RECARGA_COMPLETA = "recarga_completa"
    ATUALIZAR_TRANSITO = "atualizar_transito"
    ESTRADA_BLOQUEADA = "estrada_bloqueada"
    ESTACAO_AVARIADA = "estacao_avariada"


@dataclass
class SimulationEvent:
    """Evento na simulação."""
    tempo: float
    tipo: EventType
    dados: Dict
    
    def __lt__(self, other):
        """Comparação para heap de prioridade."""
        return self.tempo < other.tempo


class TaxiSimulator:
    """
    Simulador de operação da frota TaxiGreen.
    
    Simula:
    - Chegada dinâmica de pedidos
    - Movimentação de veículos
    - Recargas e abastecimentos
    - Eventos aleatórios (trânsito, avarias)
    - Atualização de autonomia
    """
    
    def __init__(
        self,
        frota: List[Vehicle],
        cidade: City,
        config: dict,
        estrategia_alocacao: Optional[Callable] = None,
        seed: Optional[int] = None
    ):
        """
        Inicializa simulador.
        
        Args:
            frota: Lista de veículos
            cidade: Grafo da cidade
            config: Configurações do sistema
            estrategia_alocacao: Função que aloca veículos a pedidos
            seed: Semente para geração aleatória
        """
        self.frota = {v.id: v for v in frota}
        self.cidade = cidade
        self.config = config
        self.estrategia_alocacao = estrategia_alocacao
        
        # Estado da simulação
        self.tempo_atual = 0.0
        self.eventos: List[SimulationEvent] = []
        self.pedidos_pendentes: List[Request] = []
        self.pedidos_em_servico: Dict[str, Request] = {}
        self.pedidos_completos: List[Request] = []
        
        # Métricas
        self.metricas = MetricsCollector()
        
        # Gerador aleatório
        if seed is not None:
            random.seed(seed)
        
        # Registrar veículos nas métricas
        for veiculo in frota:
            self.metricas.registrar_veiculo(veiculo.id)
    
    def adicionar_pedido(self, pedido: Request, tempo: Optional[float] = None):
        """
        Adiciona pedido à simulação.
        
        Args:
            pedido: Pedido a adicionar
            tempo: Tempo de chegada (None = tempo atual)
        """
        tempo_chegada = tempo if tempo is not None else self.tempo_atual
        
        evento = SimulationEvent(
            tempo=tempo_chegada,
            tipo=EventType.NOVO_PEDIDO,
            dados={'pedido': pedido}
        )
        
        self._inserir_evento(evento)
    
    def gerar_pedidos_aleatorios(
        self,
        num_pedidos: int,
        tempo_maximo: float,
        distribuicao: str = 'uniforme'
    ):
        """
        Gera pedidos aleatórios ao longo do tempo.
        
        Args:
            num_pedidos: Número de pedidos a gerar
            tempo_maximo: Tempo máximo da simulação
            distribuicao: 'uniforme' ou 'poisson'
        """
        if distribuicao == 'uniforme':
            tempos = sorted([random.uniform(0, tempo_maximo) for _ in range(num_pedidos)])
        else:  # poisson-like
            tempos = []
            t = 0
            while len(tempos) < num_pedidos and t < tempo_maximo:
                intervalo = random.expovariate(num_pedidos / tempo_maximo)
                t += intervalo
                if t < tempo_maximo:
                    tempos.append(t)
        
        # Gerar pedidos
        nodes = list(self.cidade.nodes)
        if len(nodes) < 2:
            print("⚠️  Cidade precisa ter pelo menos 2 nós para gerar pedidos")
            return
        
        for i, tempo in enumerate(tempos):
            origem, destino = random.sample(nodes, 2)
            
            pedido = Request(
                request_id=f"REQ{i+1:03d}",
                origem=origem,
                destino=destino,
                num_passageiros=random.choice([1, 1, 2, 3]),  # Mais pedidos de 1 passageiro
                horario_pedido=tempo,
                prioridade=random.choices(
                    [Priority.NORMAL, Priority.URGENT, Priority.PREMIUM],
                    weights=[0.7, 0.2, 0.1]
                )[0],
                preferencia_ambiental=random.choices(
                    [EnvironmentalPreference.YES, EnvironmentalPreference.NO, EnvironmentalPreference.INDIFFERENT],
                    weights=[0.3, 0.2, 0.5]
                )[0]
            )
            
            self.adicionar_pedido(pedido, tempo)
    
    def executar(self, tempo_total: float, verbose: bool = False):
        """
        Executa simulação até tempo_total.
        
        Args:
            tempo_total: Tempo total de simulação (minutos)
            verbose: Se True, imprime eventos
        """
        self.metricas.iniciar_simulacao()
        
        if verbose:
            print(f"\n🚀 Iniciando simulação - {tempo_total} minutos")
            print(f"🚗 Frota: {len(self.frota)} veículos")
            print(f"📋 Eventos agendados: {len(self.eventos)}\n")
        
        while self.eventos and self.tempo_atual < tempo_total:
            # Obter próximo evento
            evento = self._proximo_evento()
            
            if evento.tempo > tempo_total:
                break
            
            # Avançar tempo
            self.tempo_atual = evento.tempo
            
            # Processar evento
            if verbose:
                print(f"[{self.tempo_atual:7.1f}min] {evento.tipo.value}")
            
            self._processar_evento(evento, verbose)
        
        # Finalizar simulação
        self.tempo_atual = tempo_total
        self.metricas.finalizar_simulacao(tempo_total)
        
        if verbose:
            print(f"\n✅ Simulação concluída - {tempo_total} minutos")
    
    def _processar_evento(self, evento: SimulationEvent, verbose: bool = False):
        """Processa um evento."""
        if evento.tipo == EventType.NOVO_PEDIDO:
            self._processar_novo_pedido(evento, verbose)
        
        elif evento.tipo == EventType.VEICULO_CHEGOU_CLIENTE:
            self._processar_chegada_cliente(evento, verbose)
        
        elif evento.tipo == EventType.VEICULO_CHEGOU_DESTINO:
            self._processar_chegada_destino(evento, verbose)
        
        elif evento.tipo == EventType.RECARGA_COMPLETA:
            self._processar_recarga_completa(evento, verbose)
        
        elif evento.tipo == EventType.ATUALIZAR_TRANSITO:
            self._processar_atualizacao_transito(evento, verbose)
        
        elif evento.tipo == EventType.ESTRADA_BLOQUEADA:
            self._processar_bloqueio_estrada(evento, verbose)
        
        elif evento.tipo == EventType.ESTACAO_AVARIADA:
            self._processar_avaria_estacao(evento, verbose)
    
    def _processar_novo_pedido(self, evento: SimulationEvent, verbose: bool):
        """Processa chegada de novo pedido."""
        pedido = evento.dados['pedido']
        self.pedidos_pendentes.append(pedido)
        
        # Registrar nas métricas
        self.metricas.registrar_pedido(pedido.id, self.tempo_atual)
        
        if verbose:
            print(f"    📞 Novo pedido {pedido.id}: {pedido.origem} → {pedido.destino}")
        
        # Tentar alocar imediatamente
        self._tentar_alocar_pedidos(verbose)
    
    def _tentar_alocar_pedidos(self, verbose: bool = False):
        """Tenta alocar veículos disponíveis aos pedidos pendentes."""
        pedidos_alocados = []
        
        for pedido in self.pedidos_pendentes:
            # Encontrar veículo disponível
            veiculo = self._encontrar_melhor_veiculo(pedido)
            
            if veiculo:
                # Alocar veículo
                self._alocar_veiculo(veiculo, pedido, verbose)
                pedidos_alocados.append(pedido)
        
        # Remover pedidos alocados da lista de pendentes
        for pedido in pedidos_alocados:
            self.pedidos_pendentes.remove(pedido)
    
    def _encontrar_melhor_veiculo(self, pedido: Request) -> Optional[Vehicle]:
        """
        Encontra melhor veículo para atender pedido.
        
        Critérios:
        - Disponível
        - Capacidade suficiente
        - Autonomia suficiente
        - Mais próximo (ou usar estratégia customizada)
        """
        candidatos = []
        
        for veiculo in self.frota.values():
            if veiculo.estado != VehicleState.AVAILABLE:
                continue
            
            # Verificar capacidade
            if veiculo.capacidade < pedido.num_passageiros:
                continue
            
            # Calcular distâncias
            dist_to_pickup = self._calcular_distancia(veiculo.localizacao, pedido.origem)
            dist_trip = self._calcular_distancia(pedido.origem, pedido.destino)
            
            # Verificar autonomia (com margem de 20%)
            if veiculo.autonomia_atual < (dist_to_pickup + dist_trip) * 1.2:
                continue
            
            # Preferência ambiental
            score = dist_to_pickup  # Menor distância = melhor
            if pedido.preferencia_ambiental and veiculo.tipo == VehicleType.ELECTRIC:
                score *= 0.7  # Bónus para elétricos
            
            candidatos.append((score, veiculo))
        
        if not candidatos:
            return None
        
        # Ordenar por score e retornar melhor
        candidatos.sort(key=lambda x: x[0])
        return candidatos[0][1]
    
    def _alocar_veiculo(self, veiculo: Vehicle, pedido: Request, verbose: bool = False):
        """Aloca veículo a pedido e agenda eventos."""
        # Atualizar estado do veículo
        veiculo.estado = VehicleState.OCCUPIED
        
        # Registrar alocação
        self.metricas.registrar_alocacao(pedido.id, veiculo.id, self.tempo_atual)
        self.pedidos_em_servico[pedido.id] = pedido
        
        if verbose:
            print(f"    ✅ Alocado {veiculo.id} ao pedido {pedido.id}")
        
        # Calcular tempo até cliente
        dist_to_pickup = self._calcular_distancia(veiculo.localizacao, pedido.origem)
        tempo_viagem = self._calcular_tempo_viagem(veiculo.localizacao, pedido.origem)
        
        # Agendar chegada ao cliente
        evento_chegada = SimulationEvent(
            tempo=self.tempo_atual + tempo_viagem,
            tipo=EventType.VEICULO_CHEGOU_CLIENTE,
            dados={
                'veiculo_id': veiculo.id,
                'pedido_id': pedido.id,
                'distancia': dist_to_pickup
            }
        )
        self._inserir_evento(evento_chegada)
    
    def _processar_chegada_cliente(self, evento: SimulationEvent, verbose: bool):
        """Processa chegada do veículo ao cliente."""
        veiculo_id = evento.dados['veiculo_id']
        pedido_id = evento.dados['pedido_id']
        dist_vazia = evento.dados['distancia']
        
        veiculo = self.frota[veiculo_id]
        pedido = self.pedidos_em_servico[pedido_id]
        
        if verbose:
            print(f"    🚗 {veiculo_id} chegou ao cliente em {pedido.origem}")
        
        # Atualizar posição e autonomia
        veiculo.localizacao = pedido.origem
        veiculo.consumir_autonomia(dist_vazia)
        
        # Calcular tempo de viagem até destino
        dist_trip = self._calcular_distancia(pedido.origem, pedido.destino)
        tempo_trip = self._calcular_tempo_viagem(pedido.origem, pedido.destino)
        
        # Agendar chegada ao destino
        evento_destino = SimulationEvent(
            tempo=self.tempo_atual + tempo_trip,
            tipo=EventType.VEICULO_CHEGOU_DESTINO,
            dados={
                'veiculo_id': veiculo_id,
                'pedido_id': pedido_id,
                'distancia_vazia': dist_vazia,
                'distancia_viagem': dist_trip
            }
        )
        self._inserir_evento(evento_destino)
    
    def _processar_chegada_destino(self, evento: SimulationEvent, verbose: bool):
        """Processa chegada ao destino."""
        veiculo_id = evento.dados['veiculo_id']
        pedido_id = evento.dados['pedido_id']
        dist_vazia = evento.dados['distancia_vazia']
        dist_trip = evento.dados['distancia_viagem']
        
        veiculo = self.frota[veiculo_id]
        pedido = self.pedidos_em_servico.pop(pedido_id)
        
        if verbose:
            print(f"    🎯 {veiculo_id} completou pedido {pedido_id} em {pedido.destino}")
        
        # Atualizar posição e autonomia
        veiculo.localizacao = pedido.destino
        veiculo.consumir_autonomia(dist_trip)
        veiculo.estado = VehicleState.AVAILABLE
        
        # Calcular custo e emissões
        dist_total = dist_vazia + dist_trip
        custo = dist_total * veiculo.custo_km
        emissoes = veiculo.calcular_emissoes(dist_total)
        
        # Registrar conclusão
        self.metricas.registrar_conclusao_pedido(
            pedido_id,
            self.tempo_atual,
            dist_vazia,
            dist_total,
            custo,
            emissoes
        )
        
        self.pedidos_completos.append(pedido)
        
        # Verificar se precisa recarregar
        if veiculo.precisa_recarga():
            self._agendar_recarga(veiculo)
        else:
            # Tentar alocar próximo pedido
            self._tentar_alocar_pedidos(verbose)
    
    def _agendar_recarga(self, veiculo: Vehicle):
        """Agenda recarga de veículo."""
        veiculo.estado = VehicleState.CHARGING
        
        # Tempo de recarga
        if veiculo.tipo == VehicleType.ELECTRIC:
            tempo_recarga = 45.0  # 45 minutos
        else:
            tempo_recarga = 10.0  # 10 minutos
        
        # Agendar conclusão da recarga
        evento = SimulationEvent(
            tempo=self.tempo_atual + tempo_recarga,
            tipo=EventType.RECARGA_COMPLETA,
            dados={'veiculo_id': veiculo.id, 'tempo_recarga': tempo_recarga}
        )
        self._inserir_evento(evento)
        
        self.metricas.registrar_recarga(veiculo.id)
    
    def _processar_recarga_completa(self, evento: SimulationEvent, verbose: bool):
        """Processa conclusão de recarga."""
        veiculo_id = evento.dados['veiculo_id']
        tempo_recarga = evento.dados['tempo_recarga']
        
        veiculo = self.frota[veiculo_id]
        veiculo.autonomia_atual = veiculo.autonomia_maxima
        veiculo.estado = VehicleState.AVAILABLE
        
        if verbose:
            print(f"    🔋 {veiculo_id} recarga completa")
        
        # Registrar tempo de recarga
        self.metricas.registrar_tempo_veiculo(veiculo_id, tempo_recarga=tempo_recarga)
        
        # Tentar alocar pedidos pendentes
        self._tentar_alocar_pedidos(verbose)
    
    def _processar_atualizacao_transito(self, evento: SimulationEvent, verbose: bool):
        """Processa atualização de trânsito."""
        # Implementação futura: atualizar fatores de trânsito
        pass
    
    def _processar_bloqueio_estrada(self, evento: SimulationEvent, verbose: bool):
        """Processa bloqueio de estrada."""
        # Implementação futura: bloquear arestas específicas
        pass
    
    def _processar_avaria_estacao(self, evento: SimulationEvent, verbose: bool):
        """Processa avaria em estação."""
        # Implementação futura: marcar estações como indisponíveis
        pass
    
    def _calcular_distancia(self, origem: str, destino: str) -> float:
        """Calcula distância entre dois nós."""
        if origem == destino:
            return 0.0
        
        aresta = self.cidade.obter_aresta(origem, destino)
        if aresta:
            return aresta.distancia
        
        # Usar coordenadas se disponível
        if hasattr(self.cidade, 'coordenadas'):
            coords = self.cidade.coordenadas
            if origem in coords and destino in coords:
                import math
                x1, y1 = coords[origem]
                x2, y2 = coords[destino]
                return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        
        return 10.0  # Default
    
    def _calcular_tempo_viagem(self, origem: str, destino: str) -> float:
        """Calcula tempo de viagem entre dois nós (em minutos)."""
        if origem == destino:
            return 0.0
        
        aresta = self.cidade.obter_aresta(origem, destino)
        if aresta:
            return aresta.tempo_viagem()
        
        # Estimar baseado em distância
        dist = self._calcular_distancia(origem, destino)
        return (dist / 40.0) * 60.0  # 40 km/h em minutos
    
    def _inserir_evento(self, evento: SimulationEvent):
        """Insere evento mantendo ordem temporal."""
        self.eventos.append(evento)
        self.eventos.sort(key=lambda e: e.tempo)
    
    def _proximo_evento(self) -> SimulationEvent:
        """Remove e retorna próximo evento."""
        return self.eventos.pop(0)
    
    def obter_estado_atual(self) -> Dict:
        """Retorna estado atual da simulação."""
        return {
            'tempo_atual': self.tempo_atual,
            'pedidos_pendentes': len(self.pedidos_pendentes),
            'pedidos_em_servico': len(self.pedidos_em_servico),
            'pedidos_completos': len(self.pedidos_completos),
            'veiculos_disponiveis': sum(1 for v in self.frota.values() if v.estado == VehicleState.AVAILABLE),
            'veiculos_ocupados': sum(1 for v in self.frota.values() if v.estado == VehicleState.OCCUPIED),
            'veiculos_recarga': sum(1 for v in self.frota.values() if v.estado == VehicleState.CHARGING)
        }
    
    def obter_relatorio_metricas(self) -> Dict:
        """Retorna relatório completo de métricas."""
        return self.metricas.gerar_relatorio_completo()
    
    def imprimir_resumo(self):
        """Imprime resumo da simulação."""
        self.metricas.imprimir_resumo()

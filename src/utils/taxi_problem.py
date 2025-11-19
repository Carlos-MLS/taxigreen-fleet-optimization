"""
Problema de alocação e roteamento de táxis.
Modela o problema específico de gestão de frota TaxiGreen.
"""

from typing import List, Tuple, Dict, Optional, Set
from dataclasses import dataclass, field
from copy import deepcopy
import math

from .problem import Problem
from ..models.vehicle import Vehicle, VehicleState
from ..models.request import Request, Priority
from ..models.city import City


@dataclass
class TaxiState:
    """
    Representa o estado do sistema de táxis.
    
    Attributes:
        vehicle_positions: Posições atuais dos veículos {vehicle_id: node_id}
        vehicle_autonomy: Autonomia restante {vehicle_id: km}
        vehicle_states: Estados dos veículos {vehicle_id: VehicleState}
        pending_requests: Pedidos ainda não atendidos
        assigned_requests: Pedidos já alocados {request_id: vehicle_id}
        rejected_requests: Pedidos rejeitados
        current_time: Tempo atual da simulação (minutos)
        total_cost: Custo acumulado
        total_emissions: Emissões acumuladas (kg CO2)
        empty_km: Km percorridos sem passageiros
    """
    vehicle_positions: Dict[str, str]
    vehicle_autonomy: Dict[str, float]
    vehicle_states: Dict[str, VehicleState]
    pending_requests: List[Request]
    assigned_requests: Dict[str, str] = field(default_factory=dict)
    rejected_requests: Set[str] = field(default_factory=set)
    current_time: float = 0.0
    total_cost: float = 0.0
    total_emissions: float = 0.0
    empty_km: float = 0.0
    
    def __hash__(self):
        """Hash para uso em conjuntos explored."""
        return hash((
            tuple(sorted(self.vehicle_positions.items())),
            len(self.pending_requests),
            len(self.assigned_requests),
            len(self.rejected_requests)
        ))


@dataclass
class TaxiAction:
    """
    Ação no problema de táxis.
    
    Types:
        - ALLOCATE: Alocar veículo a pedido
        - MOVE: Mover veículo vazio para localização
        - TRANSPORT: Transportar passageiros
        - RECHARGE: Recarregar/reabastecer veículo
        - REJECT: Rejeitar pedido
        - WAIT: Aguardar
    """
    action_type: str  # ALLOCATE, MOVE, TRANSPORT, RECHARGE, REJECT, WAIT
    vehicle_id: Optional[str] = None
    request_id: Optional[str] = None
    destination: Optional[str] = None
    station_id: Optional[str] = None
    
    def __str__(self):
        if self.action_type == "ALLOCATE":
            return f"Alocar {self.vehicle_id} ao pedido {self.request_id}"
        elif self.action_type == "MOVE":
            return f"Mover {self.vehicle_id} para {self.destination}"
        elif self.action_type == "TRANSPORT":
            return f"Transportar com {self.vehicle_id} até {self.destination}"
        elif self.action_type == "RECHARGE":
            return f"Recarregar {self.vehicle_id} na estação {self.station_id}"
        elif self.action_type == "REJECT":
            return f"Rejeitar pedido {self.request_id}"
        elif self.action_type == "WAIT":
            return f"Aguardar com {self.vehicle_id}"
        return f"Action({self.action_type})"


class TaxiProblem(Problem):
    """
    Problema de alocação e roteamento de táxis.
    
    Estado: Posições dos veículos, autonomia, pedidos pendentes
    Objetivo: Atender todos os pedidos minimizando custos
    Ações: Alocar, mover, transportar, recarregar, rejeitar
    """
    
    def __init__(
        self,
        vehicles: List[Vehicle],
        requests: List[Request],
        city: City,
        config: dict,
        max_time: float = 480.0  # 8 horas
    ):
        """
        Inicializa o problema de táxis.
        
        Args:
            vehicles: Lista de veículos da frota
            requests: Lista de pedidos a atender
            city: Grafo da cidade
            config: Configurações do sistema
            max_time: Tempo máximo de simulação (minutos)
        """
        # Criar estado inicial
        initial = TaxiState(
            vehicle_positions={v.id: v.localizacao_atual for v in vehicles},
            vehicle_autonomy={v.id: v.autonomia_atual for v in vehicles},
            vehicle_states={v.id: v.estado for v in vehicles},
            pending_requests=list(requests),
            current_time=0.0
        )
        
        super().__init__(initial, None)
        
        self.vehicles = {v.id: v for v in vehicles}
        self.city = city
        self.config = config
        self.max_time = max_time
        
        # Cache de distâncias (para otimização)
        self._distance_cache: Dict[Tuple[str, str], float] = {}
    
    def initial_state(self) -> TaxiState:
        """Retorna estado inicial."""
        return self.initial
    
    def goal_test(self, state: TaxiState) -> bool:
        """
        Testa se atingiu objetivo.
        
        Objetivo: Todos os pedidos atendidos ou rejeitados (com justificação).
        """
        total_requests = len(state.pending_requests) + len(state.assigned_requests) + len(state.rejected_requests)
        
        # Todos os pedidos processados
        if len(state.pending_requests) == 0:
            return True
        
        # Tempo excedido
        if state.current_time >= self.max_time:
            return True
        
        return False
    
    def actions(self, state: TaxiState) -> List[TaxiAction]:
        """
        Retorna ações possíveis no estado atual.
        
        Considera:
        - Alocar veículos disponíveis a pedidos pendentes
        - Recarregar veículos com autonomia baixa
        - Rejeitar pedidos impossíveis
        """
        actions = []
        
        # Para cada pedido pendente
        for request in state.pending_requests:
            # Tentar alocar veículos disponíveis
            for vehicle_id, vehicle in self.vehicles.items():
                if state.vehicle_states[vehicle_id] == VehicleState.AVAILABLE:
                    # Verificar se veículo pode atender
                    if self._can_serve_request(state, vehicle_id, request):
                        actions.append(TaxiAction(
                            action_type="ALLOCATE",
                            vehicle_id=vehicle_id,
                            request_id=request.id
                        ))
            
            # Opção de rejeitar pedido se impossível
            if not self._any_vehicle_can_serve(state, request):
                actions.append(TaxiAction(
                    action_type="REJECT",
                    request_id=request.id
                ))
        
        # Ações de recarga para veículos com autonomia baixa
        for vehicle_id, vehicle in self.vehicles.items():
            if state.vehicle_states[vehicle_id] == VehicleState.AVAILABLE:
                if state.vehicle_autonomy[vehicle_id] < vehicle.autonomia_maxima * 0.3:
                    # Encontrar estação mais próxima
                    station = self._find_nearest_station(
                        state.vehicle_positions[vehicle_id],
                        vehicle.tipo
                    )
                    if station:
                        actions.append(TaxiAction(
                            action_type="RECHARGE",
                            vehicle_id=vehicle_id,
                            station_id=station
                        ))
        
        # Se não há ações, aguardar
        if not actions:
            actions.append(TaxiAction(action_type="WAIT"))
        
        return actions
    
    def result(self, state: TaxiState, action: TaxiAction) -> TaxiState:
        """
        Aplica ação e retorna novo estado.
        
        Args:
            state: Estado atual
            action: Ação a aplicar
            
        Returns:
            Novo estado após aplicar ação
        """
        new_state = deepcopy(state)
        
        if action.action_type == "ALLOCATE":
            self._apply_allocate(new_state, action)
        elif action.action_type == "RECHARGE":
            self._apply_recharge(new_state, action)
        elif action.action_type == "REJECT":
            self._apply_reject(new_state, action)
        elif action.action_type == "WAIT":
            new_state.current_time += 1.0  # Aguardar 1 minuto
        
        return new_state
    
    def step_cost(self, state: TaxiState, action: TaxiAction, next_state: TaxiState) -> float:
        """
        Calcula custo de aplicar ação.
        
        Custo multiobjetivo:
        - Tempo de resposta
        - Distância
        - Custo operacional
        - Km vazios
        - Emissões
        - Penalização por rejeição
        """
        cost = 0.0
        
        if action.action_type == "ALLOCATE":
            request = self._get_request_by_id(state.pending_requests, action.request_id)
            vehicle = self.vehicles[action.vehicle_id]
            
            # Distância vazia até cliente
            dist_to_pickup = self._get_distance(
                state.vehicle_positions[action.vehicle_id],
                request.origem
            )
            
            # Distância da viagem
            dist_trip = self._get_distance(request.origem, request.destino)
            
            # Tempo total
            time_to_pickup = dist_to_pickup / 40.0 * 60  # 40 km/h em minutos
            time_trip = dist_trip / 40.0 * 60
            total_time = time_to_pickup + time_trip
            
            # Custo operacional
            operational_cost = (dist_to_pickup + dist_trip) * vehicle.custo_por_km
            
            # Emissões
            emissions = (dist_to_pickup + dist_trip) * vehicle.emissoes_co2_por_km
            
            # Pesos da função de custo
            w_time = self.config.get('PESO_TEMPO_RESPOSTA', 0.30)
            w_distance = self.config.get('PESO_DISTANCIA', 0.25)
            w_cost = self.config.get('PESO_CUSTO', 0.20)
            w_empty = self.config.get('PESO_KM_VAZIOS', 0.15)
            w_emissions = self.config.get('PESO_EMISSOES', 0.10)
            
            cost = (
                w_time * total_time +
                w_distance * (dist_to_pickup + dist_trip) +
                w_cost * operational_cost +
                w_empty * dist_to_pickup +
                w_emissions * emissions
            )
            
            # Bónus para prioridade alta
            if request.prioridade == Priority.URGENT:
                cost *= 0.8
            elif request.prioridade == Priority.PREMIUM:
                cost *= 0.7
        
        elif action.action_type == "RECHARGE":
            # Custo de tempo de recarga
            vehicle = self.vehicles[action.vehicle_id]
            if vehicle.tipo.name == "ELETRICO":
                cost = 45.0  # 45 minutos
            else:
                cost = 10.0  # 10 minutos
        
        elif action.action_type == "REJECT":
            # Penalização alta por rejeitar pedido
            request = self._get_request_by_id(state.pending_requests, action.request_id)
            penalty = 1000.0
            if request.prioridade == Priority.URGENT:
                penalty *= 2.0
            elif request.prioridade == Priority.PREMIUM:
                penalty *= 3.0
            cost = penalty
        
        elif action.action_type == "WAIT":
            cost = 1.0  # Pequeno custo por aguardar
        
        return cost
    
    def heuristic(self, state: TaxiState) -> float:
        """
        Heurística: estimativa do custo para completar pedidos pendentes.
        
        Usa distância mínima de veículos disponíveis aos pedidos.
        """
        if len(state.pending_requests) == 0:
            return 0.0
        
        # Veículos disponíveis
        available_vehicles = [
            vid for vid, vstate in state.vehicle_states.items()
            if vstate == VehicleState.AVAILABLE
        ]
        
        if not available_vehicles:
            # Sem veículos disponíveis = custo alto
            return len(state.pending_requests) * 1000.0
        
        total_h = 0.0
        
        for request in state.pending_requests:
            # Distância mínima de qualquer veículo ao pedido
            min_dist = float('inf')
            
            for vid in available_vehicles:
                dist = self._get_distance(
                    state.vehicle_positions[vid],
                    request.origem
                )
                min_dist = min(min_dist, dist)
            
            # Distância da viagem
            trip_dist = self._get_distance(request.origem, request.destino)
            
            # Estimativa de custo
            total_h += (min_dist + trip_dist) * 0.5  # Simplificado
        
        return total_h
    
    # Métodos auxiliares privados
    
    def _can_serve_request(self, state: TaxiState, vehicle_id: str, request: Request) -> bool:
        """Verifica se veículo pode atender pedido."""
        vehicle = self.vehicles[vehicle_id]
        
        # Capacidade suficiente
        if vehicle.capacidade_passageiros < request.num_passageiros:
            return False
        
        # Distância até origem
        dist_to_pickup = self._get_distance(
            state.vehicle_positions[vehicle_id],
            request.origem
        )
        
        # Distância da viagem
        dist_trip = self._get_distance(request.origem, request.destino)
        
        # Autonomia suficiente (com margem)
        total_dist = dist_to_pickup + dist_trip
        if state.vehicle_autonomy[vehicle_id] < total_dist * 1.2:
            return False
        
        # Preferência ambiental
        if request.preferencia_ambiental and not vehicle.tipo.name == "ELETRICO":
            # Permite mas com penalização no custo
            pass
        
        return True
    
    def _any_vehicle_can_serve(self, state: TaxiState, request: Request) -> bool:
        """Verifica se algum veículo pode atender pedido."""
        for vehicle_id in self.vehicles.keys():
            if state.vehicle_states[vehicle_id] == VehicleState.AVAILABLE:
                if self._can_serve_request(state, vehicle_id, request):
                    return True
        return False
    
    def _get_distance(self, origin: str, destination: str) -> float:
        """Obtém distância entre dois nós (com cache)."""
        if origin == destination:
            return 0.0
        
        key = (origin, destination)
        if key in self._distance_cache:
            return self._distance_cache[key]
        
        # Buscar no grafo
        edge = self.city.obter_aresta(origin, destination)
        if edge:
            dist = edge.distancia
        else:
            # Usar coordenadas se disponível
            if hasattr(self.city, 'coordenadas'):
                coords = self.city.coordenadas
                if origin in coords and destination in coords:
                    x1, y1 = coords[origin]
                    x2, y2 = coords[destination]
                    dist = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
                else:
                    dist = 999.0  # Distância alta se não encontrar
            else:
                dist = 999.0
        
        self._distance_cache[key] = dist
        return dist
    
    def _find_nearest_station(self, location: str, vehicle_type) -> Optional[str]:
        """Encontra estação mais próxima compatível com tipo de veículo."""
        # Implementação simplificada
        # Em implementação real, procurar nas estações da cidade
        return None  # Por agora
    
    def _get_request_by_id(self, requests: List[Request], request_id: str) -> Optional[Request]:
        """Encontra pedido por ID."""
        for req in requests:
            if req.id == request_id:
                return req
        return None
    
    def _apply_allocate(self, state: TaxiState, action: TaxiAction):
        """Aplica ação de alocação."""
        request = self._get_request_by_id(state.pending_requests, action.request_id)
        vehicle = self.vehicles[action.vehicle_id]
        
        # Calcular distâncias
        dist_to_pickup = self._get_distance(
            state.vehicle_positions[action.vehicle_id],
            request.origem
        )
        dist_trip = self._get_distance(request.origem, request.destino)
        
        # Atualizar estado
        state.vehicle_positions[action.vehicle_id] = request.destino
        state.vehicle_autonomy[action.vehicle_id] -= (dist_to_pickup + dist_trip)
        state.vehicle_states[action.vehicle_id] = VehicleState.AVAILABLE  # Volta a ficar disponível
        
        # Remover pedido de pendentes e adicionar a atendidos
        state.pending_requests = [r for r in state.pending_requests if r.id != request.id]
        state.assigned_requests[request.id] = action.vehicle_id
        
        # Atualizar tempo
        time_elapsed = (dist_to_pickup + dist_trip) / 40.0 * 60  # 40 km/h
        state.current_time += time_elapsed
        
        # Atualizar custos
        state.total_cost += (dist_to_pickup + dist_trip) * vehicle.custo_por_km
        state.total_emissions += (dist_to_pickup + dist_trip) * vehicle.emissoes_co2_por_km
        state.empty_km += dist_to_pickup
    
    def _apply_recharge(self, state: TaxiState, action: TaxiAction):
        """Aplica ação de recarga."""
        vehicle = self.vehicles[action.vehicle_id]
        
        # Restaurar autonomia
        state.vehicle_autonomy[action.vehicle_id] = vehicle.autonomia_maxima
        
        # Atualizar tempo
        if vehicle.tipo.name == "ELETRICO":
            state.current_time += 45.0  # 45 minutos
        else:
            state.current_time += 10.0  # 10 minutos
        
        state.vehicle_states[action.vehicle_id] = VehicleState.AVAILABLE
    
    def _apply_reject(self, state: TaxiState, action: TaxiAction):
        """Aplica ação de rejeição."""
        state.pending_requests = [r for r in state.pending_requests if r.id != action.request_id]
        state.rejected_requests.add(action.request_id)

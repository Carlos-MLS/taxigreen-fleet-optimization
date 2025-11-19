"""
Classe abstrata base para problemas de procura.
Define a interface que todos os problemas devem implementar.
"""

from abc import ABC, abstractmethod
from typing import List, Tuple, Any, Optional


class Problem(ABC):
    """
    Classe abstrata para definir um problema de procura.
    
    Subclasses devem implementar:
    - initial_state(): Estado inicial
    - goal_test(state): Teste objetivo
    - actions(state): Ações disponíveis
    - result(state, action): Estado resultante
    - step_cost(state, action, next_state): Custo de uma ação
    """
    
    def __init__(self, initial_state: Any, goal_state: Optional[Any] = None):
        """
        Inicializa o problema.
        
        Args:
            initial_state: Estado inicial do problema
            goal_state: Estado objetivo (opcional, pode ser testado de outra forma)
        """
        self.initial = initial_state
        self.goal = goal_state
    
    @abstractmethod
    def initial_state(self) -> Any:
        """
        Retorna o estado inicial do problema.
        
        Returns:
            Estado inicial
        """
        pass
    
    @abstractmethod
    def goal_test(self, state: Any) -> bool:
        """
        Testa se um estado é objetivo.
        
        Args:
            state: Estado a testar
            
        Returns:
            True se é estado objetivo
        """
        pass
    
    @abstractmethod
    def actions(self, state: Any) -> List[Any]:
        """
        Retorna as ações disponíveis num estado.
        
        Args:
            state: Estado atual
            
        Returns:
            Lista de ações possíveis
        """
        pass
    
    @abstractmethod
    def result(self, state: Any, action: Any) -> Any:
        """
        Retorna o estado resultante de aplicar uma ação.
        
        Args:
            state: Estado atual
            action: Ação a aplicar
            
        Returns:
            Novo estado
        """
        pass
    
    @abstractmethod
    def step_cost(self, state: Any, action: Any, next_state: Any) -> float:
        """
        Custo de executar uma ação.
        
        Args:
            state: Estado atual
            action: Ação executada
            next_state: Estado resultante
            
        Returns:
            Custo da ação
        """
        pass
    
    def heuristic(self, state: Any) -> float:
        """
        Função heurística (para procura informada).
        Por defeito retorna 0 (pode ser sobrescrita).
        
        Args:
            state: Estado atual
            
        Returns:
            Estimativa de custo até objetivo
        """
        return 0.0
    
    def path_cost(self, cost_so_far: float, state: Any, action: Any, next_state: Any) -> float:
        """
        Calcula o custo total do caminho.
        
        Args:
            cost_so_far: Custo acumulado até agora
            state: Estado atual
            action: Ação executada
            next_state: Estado resultante
            
        Returns:
            Novo custo total
        """
        return cost_so_far + self.step_cost(state, action, next_state)


class RouteProblem(Problem):
    """
    Problema de encontrar rota entre dois pontos num grafo.
    Útil para problemas de caminho mais curto.
    """
    
    def __init__(self, graph: Any, initial_node: str, goal_node: str):
        """
        Inicializa problema de rota.
        
        Args:
            graph: Grafo (objeto City)
            initial_node: Nó inicial
            goal_node: Nó objetivo
        """
        super().__init__(initial_node, goal_node)
        self.graph = graph
        self.start = initial_node
        self.goal_node = goal_node
    
    def initial_state(self) -> str:
        """Retorna nó inicial."""
        return self.start
    
    def goal_test(self, state: str) -> bool:
        """Testa se chegou ao objetivo."""
        return state == self.goal_node
    
    def actions(self, state: str) -> List[str]:
        """Retorna nós vizinhos acessíveis."""
        vizinhos = self.graph.obter_vizinhos(state)
        # Filtrar apenas caminhos abertos
        return [v for v in vizinhos if self.graph.existe_caminho(state, v)]
    
    def result(self, state: str, action: str) -> str:
        """Ação é mover para nó vizinho."""
        return action
    
    def step_cost(self, state: str, action: str, next_state: str) -> float:
        """Custo é o tempo de viagem."""
        edge = self.graph.obter_aresta(state, next_state)
        if edge:
            return edge.tempo_viagem()
        return float('inf')
    
    def heuristic(self, state: str) -> float:
        """
        Heurística: distância euclidiana (se coordenadas disponíveis).
        Por defeito retorna 0 (admissível).
        """
        # Pode ser sobrescrita com coordenadas reais
        return 0.0

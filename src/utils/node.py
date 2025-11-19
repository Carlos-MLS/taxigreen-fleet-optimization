"""
Classe base para representar um nó no espaço de estados.
Usado por todos os algoritmos de procura.
"""

from typing import Optional, List, Any
from dataclasses import dataclass, field


@dataclass
class Node:
    """
    Representa um nó na árvore de procura.
    
    Attributes:
        state: Estado representado por este nó
        parent: Nó pai (None se for raiz)
        action: Ação que levou do pai a este nó
        path_cost: Custo do caminho desde a raiz até este nó
        depth: Profundidade do nó na árvore
        heuristic: Valor heurístico (para procura informada)
    """
    state: Any
    parent: Optional['Node'] = None
    action: Optional[str] = None
    path_cost: float = 0.0
    depth: int = 0
    heuristic: float = 0.0
    
    def __post_init__(self):
        """Calcula profundidade automaticamente se não fornecida."""
        if self.parent is not None and self.depth == 0:
            self.depth = self.parent.depth + 1
    
    def get_path(self) -> List['Node']:
        """
        Retorna o caminho desde a raiz até este nó.
        
        Returns:
            Lista de nós do caminho
        """
        path = []
        node = self
        while node:
            path.append(node)
            node = node.parent
        return list(reversed(path))
    
    def get_solution(self) -> List[str]:
        """
        Retorna a sequência de ações desde a raiz até este nó.
        
        Returns:
            Lista de ações
        """
        path = self.get_path()
        return [node.action for node in path[1:]]  # Excluir raiz (sem ação)
    
    def f_score(self) -> float:
        """
        Calcula f(n) = g(n) + h(n) para A*.
        
        Returns:
            Valor de f
        """
        return self.path_cost + self.heuristic
    
    def __lt__(self, other: 'Node') -> bool:
        """Comparação para fila de prioridade (usado no A*)."""
        return self.f_score() < other.f_score()
    
    def __hash__(self) -> int:
        """Hash baseado no estado (para set e dict)."""
        return hash(str(self.state))
    
    def __eq__(self, other: object) -> bool:
        """Igualdade baseada no estado."""
        if not isinstance(other, Node):
            return False
        return str(self.state) == str(other.state)
    
    def __repr__(self) -> str:
        """Representação para debug."""
        return f"Node(state={self.state}, depth={self.depth}, cost={self.path_cost:.2f}, h={self.heuristic:.2f})"


@dataclass
class SearchResult:
    """
    Resultado de uma busca.
    
    Attributes:
        success: Se encontrou solução
        path: Caminho de nós até a solução
        solution: Sequência de ações
        cost: Custo total da solução
        nodes_expanded: Número de nós expandidos
        nodes_generated: Número de nós gerados
        time_elapsed: Tempo de execução (segundos)
        max_frontier_size: Tamanho máximo da fronteira
    """
    success: bool
    path: List[Node] = field(default_factory=list)
    solution: List[str] = field(default_factory=list)
    cost: float = 0.0
    nodes_expanded: int = 0
    nodes_generated: int = 0
    time_elapsed: float = 0.0
    max_frontier_size: int = 0
    
    def __str__(self) -> str:
        """Representação string do resultado."""
        if self.success:
            return (
                f"✓ Solução encontrada!\n"
                f"  Custo: {self.cost:.2f}\n"
                f"  Profundidade: {len(self.solution)}\n"
                f"  Nós expandidos: {self.nodes_expanded}\n"
                f"  Nós gerados: {self.nodes_generated}\n"
                f"  Tempo: {self.time_elapsed:.4f}s\n"
                f"  Max fronteira: {self.max_frontier_size}"
            )
        else:
            return (
                f"✗ Solução não encontrada\n"
                f"  Nós expandidos: {self.nodes_expanded}\n"
                f"  Tempo: {self.time_elapsed:.4f}s"
            )

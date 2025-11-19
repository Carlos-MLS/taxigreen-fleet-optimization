"""
Algoritmos de Procura Informada (Heurística).
Implementa A*, Greedy Best-First Search e variantes.
"""

import heapq
from typing import Set, Callable, Optional
import time

from ..utils.node import Node, SearchResult
from ..utils.problem import Problem


def a_star_search(problem: Problem, heuristic: Optional[Callable] = None, max_nodes: int = 100000) -> SearchResult:
    """
    A* Search (Procura A*).
    
    Combina custo do caminho g(n) com heurística h(n).
    f(n) = g(n) + h(n)
    
    Completo e ótimo se h for admissível.
    
    Args:
        problem: Problema a resolver
        heuristic: Função heurística (se None, usa problem.heuristic)
        max_nodes: Máximo de nós a expandir
        
    Returns:
        SearchResult com solução ou falha
    """
    start_time = time.time()
    
    # Usar heurística do problema se não fornecida
    if heuristic is None:
        heuristic = problem.heuristic
    
    # Criar nó inicial
    initial_node = Node(
        state=problem.initial_state(),
        heuristic=heuristic(problem.initial_state())
    )
    
    # Teste objetivo no estado inicial
    if problem.goal_test(initial_node.state):
        return SearchResult(
            success=True,
            path=[initial_node],
            solution=[],
            cost=0.0,
            nodes_expanded=0,
            nodes_generated=1,
            time_elapsed=time.time() - start_time
        )
    
    # Fronteira: fila de prioridade por f(n)
    frontier = [(initial_node.f_score(), 0, initial_node)]
    frontier_dict = {str(initial_node.state): initial_node}
    
    # Conjunto de estados explorados
    explored: Set[str] = set()
    
    # Métricas
    nodes_expanded = 0
    nodes_generated = 1
    max_frontier_size = 1
    counter = 1
    
    while frontier:
        # Atualizar métricas
        max_frontier_size = max(max_frontier_size, len(frontier))
        
        # Verificar limite
        if nodes_expanded >= max_nodes:
            print(f"⚠️  A*: Limite de {max_nodes} nós atingido")
            break
        
        # Remover nó com menor f(n)
        _, _, node = heapq.heappop(frontier)
        
        # Remover do dicionário
        state_str = str(node.state)
        if state_str in frontier_dict:
            del frontier_dict[state_str]
        
        # Teste objetivo
        if problem.goal_test(node.state):
            return SearchResult(
                success=True,
                path=node.get_path(),
                solution=node.get_solution(),
                cost=node.path_cost,
                nodes_expanded=nodes_expanded,
                nodes_generated=nodes_generated,
                time_elapsed=time.time() - start_time,
                max_frontier_size=max_frontier_size
            )
        
        # Adicionar aos explorados
        explored.add(state_str)
        nodes_expanded += 1
        
        # Expandir nó
        for action in problem.actions(node.state):
            # Obter estado filho
            child_state = problem.result(node.state, action)
            child_state_str = str(child_state)
            
            # Criar nó filho
            child_cost = problem.path_cost(node.path_cost, node.state, action, child_state)
            child = Node(
                state=child_state,
                parent=node,
                action=action,
                path_cost=child_cost,
                depth=node.depth + 1,
                heuristic=heuristic(child_state)
            )
            
            nodes_generated += 1
            
            # Verificar se já foi explorado
            if child_state_str not in explored:
                # Se não está na fronteira, adicionar
                if child_state_str not in frontier_dict:
                    heapq.heappush(frontier, (child.f_score(), counter, child))
                    frontier_dict[child_state_str] = child
                    counter += 1
                # Se está na fronteira mas com f menor, atualizar
                elif child.f_score() < frontier_dict[child_state_str].f_score():
                    frontier_dict[child_state_str] = child
                    heapq.heappush(frontier, (child.f_score(), counter, child))
                    counter += 1
    
    # Falha
    return SearchResult(
        success=False,
        nodes_expanded=nodes_expanded,
        nodes_generated=nodes_generated,
        time_elapsed=time.time() - start_time,
        max_frontier_size=max_frontier_size
    )


def greedy_best_first_search(problem: Problem, heuristic: Optional[Callable] = None, max_nodes: int = 100000) -> SearchResult:
    """
    Greedy Best-First Search (Procura Gulosa).
    
    Expande o nó que parece estar mais próximo do objetivo.
    Usa apenas h(n), ignorando g(n).
    
    Não é completo nem ótimo, mas pode ser muito eficiente.
    
    Args:
        problem: Problema a resolver
        heuristic: Função heurística (se None, usa problem.heuristic)
        max_nodes: Máximo de nós a expandir
        
    Returns:
        SearchResult com solução ou falha
    """
    start_time = time.time()
    
    # Usar heurística do problema se não fornecida
    if heuristic is None:
        heuristic = problem.heuristic
    
    # Criar nó inicial
    initial_node = Node(
        state=problem.initial_state(),
        heuristic=heuristic(problem.initial_state())
    )
    
    # Teste objetivo no estado inicial
    if problem.goal_test(initial_node.state):
        return SearchResult(
            success=True,
            path=[initial_node],
            solution=[],
            cost=0.0,
            nodes_expanded=0,
            nodes_generated=1,
            time_elapsed=time.time() - start_time
        )
    
    # Fronteira: fila de prioridade por h(n)
    frontier = [(initial_node.heuristic, 0, initial_node)]
    frontier_dict = {str(initial_node.state): initial_node}
    
    # Conjunto de estados explorados
    explored: Set[str] = set()
    
    # Métricas
    nodes_expanded = 0
    nodes_generated = 1
    max_frontier_size = 1
    counter = 1
    
    while frontier:
        # Atualizar métricas
        max_frontier_size = max(max_frontier_size, len(frontier))
        
        # Verificar limite
        if nodes_expanded >= max_nodes:
            print(f"⚠️  Greedy: Limite de {max_nodes} nós atingido")
            break
        
        # Remover nó com menor h(n)
        _, _, node = heapq.heappop(frontier)
        
        # Remover do dicionário
        state_str = str(node.state)
        if state_str in frontier_dict:
            del frontier_dict[state_str]
        
        # Teste objetivo
        if problem.goal_test(node.state):
            return SearchResult(
                success=True,
                path=node.get_path(),
                solution=node.get_solution(),
                cost=node.path_cost,
                nodes_expanded=nodes_expanded,
                nodes_generated=nodes_generated,
                time_elapsed=time.time() - start_time,
                max_frontier_size=max_frontier_size
            )
        
        # Adicionar aos explorados
        explored.add(state_str)
        nodes_expanded += 1
        
        # Expandir nó
        for action in problem.actions(node.state):
            # Obter estado filho
            child_state = problem.result(node.state, action)
            child_state_str = str(child_state)
            
            # Criar nó filho
            child_cost = problem.path_cost(node.path_cost, node.state, action, child_state)
            child = Node(
                state=child_state,
                parent=node,
                action=action,
                path_cost=child_cost,
                depth=node.depth + 1,
                heuristic=heuristic(child_state)
            )
            
            nodes_generated += 1
            
            # Verificar se já foi explorado
            if child_state_str not in explored:
                # Se não está na fronteira, adicionar
                if child_state_str not in frontier_dict:
                    heapq.heappush(frontier, (child.heuristic, counter, child))
                    frontier_dict[child_state_str] = child
                    counter += 1
                # Se está na fronteira mas com h menor, atualizar
                elif child.heuristic < frontier_dict[child_state_str].heuristic:
                    frontier_dict[child_state_str] = child
                    heapq.heappush(frontier, (child.heuristic, counter, child))
                    counter += 1
    
    # Falha
    return SearchResult(
        success=False,
        nodes_expanded=nodes_expanded,
        nodes_generated=nodes_generated,
        time_elapsed=time.time() - start_time,
        max_frontier_size=max_frontier_size
    )


def weighted_a_star(problem: Problem, weight: float = 1.5, heuristic: Optional[Callable] = None, max_nodes: int = 100000) -> SearchResult:
    """
    Weighted A* Search.
    
    Variante do A* que dá mais peso à heurística.
    f(n) = g(n) + w * h(n), onde w > 1
    
    Mais rápido que A* mas não garante solução ótima.
    
    Args:
        problem: Problema a resolver
        weight: Peso da heurística (w > 1)
        heuristic: Função heurística
        max_nodes: Máximo de nós a expandir
        
    Returns:
        SearchResult com solução ou falha
    """
    # Modificar heurística para incluir peso
    original_heuristic = heuristic if heuristic else problem.heuristic
    
    def weighted_heuristic(state):
        return weight * original_heuristic(state)
    
    # Executar A* com heurística ponderada
    return a_star_search(problem, heuristic=weighted_heuristic, max_nodes=max_nodes)


# Aliases
astar = a_star_search
greedy = greedy_best_first_search

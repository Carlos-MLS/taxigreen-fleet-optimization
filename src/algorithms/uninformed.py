"""
Algoritmos de procura não-informada (uninformed search).
Inclui BFS, DFS e Uniform Cost Search.
"""

from collections import deque
import heapq
import time
from typing import Optional, Callable, List, Set

from ..utils.node import Node, SearchResult
from ..utils.problem import Problem


def breadth_first_search(problem: Problem, max_nodes: int = 100000) -> SearchResult:
    """
    Breadth-First Search (Procura em Largura).
    
    Explora todos os nós a profundidade d antes de explorar nós a profundidade d+1.
    Completo e ótimo para custos uniformes.
    
    Args:
        problem: Problema a resolver
        max_nodes: Máximo de nós a expandir
        
    Returns:
        SearchResult com solução ou falha
    """
    start_time = time.time()
    
    # Criar nó inicial
    initial_node = Node(state=problem.initial_state())
    
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
    
    # Fronteira: fila FIFO
    frontier = deque([initial_node])
    
    # Conjunto de estados explorados
    explored: Set[str] = set()
    
    # Métricas
    nodes_expanded = 0
    nodes_generated = 1
    max_frontier_size = 1
    
    while frontier:
        # Atualizar métricas
        max_frontier_size = max(max_frontier_size, len(frontier))
        
        # Verificar limite
        if nodes_expanded >= max_nodes:
            print(f"⚠️  BFS: Limite de {max_nodes} nós atingido")
            break
        
        # Remover nó da fronteira
        node = frontier.popleft()
        
        # Adicionar aos explorados
        explored.add(str(node.state))
        nodes_expanded += 1
        
        # Expandir nó
        for action in problem.actions(node.state):
            # Obter estado filho
            child_state = problem.result(node.state, action)
            
            # Criar nó filho
            child_cost = problem.path_cost(node.path_cost, node.state, action, child_state)
            child = Node(
                state=child_state,
                parent=node,
                action=action,
                path_cost=child_cost,
                depth=node.depth + 1
            )
            
            nodes_generated += 1
            
            # Verificar se já foi explorado ou está na fronteira
            if str(child.state) not in explored and child not in frontier:
                # Teste objetivo
                if problem.goal_test(child.state):
                    return SearchResult(
                        success=True,
                        path=child.get_path(),
                        solution=child.get_solution(),
                        cost=child.path_cost,
                        nodes_expanded=nodes_expanded,
                        nodes_generated=nodes_generated,
                        time_elapsed=time.time() - start_time,
                        max_frontier_size=max_frontier_size
                    )
                
                frontier.append(child)
    
    # Falha
    return SearchResult(
        success=False,
        nodes_expanded=nodes_expanded,
        nodes_generated=nodes_generated,
        time_elapsed=time.time() - start_time,
        max_frontier_size=max_frontier_size
    )


def depth_first_search(problem: Problem, max_depth: int = 50, max_nodes: int = 100000) -> SearchResult:
    """
    Depth-First Search (Procura em Profundidade).
    
    Explora o caminho mais profundo primeiro.
    Não é completo (pode entrar em loops) nem ótimo.
    
    Args:
        problem: Problema a resolver
        max_depth: Profundidade máxima
        max_nodes: Máximo de nós a expandir
        
    Returns:
        SearchResult com solução ou falha
    """
    start_time = time.time()
    
    # Criar nó inicial
    initial_node = Node(state=problem.initial_state())
    
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
    
    # Fronteira: pilha LIFO
    frontier = [initial_node]
    
    # Conjunto de estados explorados
    explored: Set[str] = set()
    
    # Métricas
    nodes_expanded = 0
    nodes_generated = 1
    max_frontier_size = 1
    
    while frontier:
        # Atualizar métricas
        max_frontier_size = max(max_frontier_size, len(frontier))
        
        # Verificar limite
        if nodes_expanded >= max_nodes:
            print(f"⚠️  DFS: Limite de {max_nodes} nós atingido")
            break
        
        # Remover nó da fronteira (último = LIFO)
        node = frontier.pop()
        
        # Verificar profundidade máxima
        if node.depth >= max_depth:
            continue
        
        # Adicionar aos explorados
        explored.add(str(node.state))
        nodes_expanded += 1
        
        # Expandir nó
        for action in problem.actions(node.state):
            # Obter estado filho
            child_state = problem.result(node.state, action)
            
            # Criar nó filho
            child_cost = problem.path_cost(node.path_cost, node.state, action, child_state)
            child = Node(
                state=child_state,
                parent=node,
                action=action,
                path_cost=child_cost,
                depth=node.depth + 1
            )
            
            nodes_generated += 1
            
            # Verificar se já foi explorado
            if str(child.state) not in explored:
                # Teste objetivo
                if problem.goal_test(child.state):
                    return SearchResult(
                        success=True,
                        path=child.get_path(),
                        solution=child.get_solution(),
                        cost=child.path_cost,
                        nodes_expanded=nodes_expanded,
                        nodes_generated=nodes_generated,
                        time_elapsed=time.time() - start_time,
                        max_frontier_size=max_frontier_size
                    )
                
                frontier.append(child)
    
    # Falha
    return SearchResult(
        success=False,
        nodes_expanded=nodes_expanded,
        nodes_generated=nodes_generated,
        time_elapsed=time.time() - start_time,
        max_frontier_size=max_frontier_size
    )


def uniform_cost_search(problem: Problem, max_nodes: int = 100000) -> SearchResult:
    """
    Uniform Cost Search (Procura de Custo Uniforme).
    
    Expande o nó com menor custo de caminho.
    Completo e ótimo.
    
    Args:
        problem: Problema a resolver
        max_nodes: Máximo de nós a expandir
        
    Returns:
        SearchResult com solução ou falha
    """
    import heapq
    start_time = time.time()
    
    # Criar nó inicial
    initial_node = Node(state=problem.initial_state())
    
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
    
    # Fronteira: fila de prioridade (min-heap)
    frontier = [(initial_node.path_cost, 0, initial_node)]  # (custo, contador, nó)
    frontier_dict = {str(initial_node.state): initial_node}
    
    # Conjunto de estados explorados
    explored: Set[str] = set()
    
    # Métricas
    nodes_expanded = 0
    nodes_generated = 1
    max_frontier_size = 1
    counter = 1  # Para desempate
    
    while frontier:
        # Atualizar métricas
        max_frontier_size = max(max_frontier_size, len(frontier))
        
        # Verificar limite
        if nodes_expanded >= max_nodes:
            print(f"⚠️  UCS: Limite de {max_nodes} nós atingido")
            break
        
        # Remover nó com menor custo
        _, _, node = heapq.heappop(frontier)
        
        # Remover do dicionário da fronteira
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
                depth=node.depth + 1
            )
            
            nodes_generated += 1
            
            # Verificar se já foi explorado
            if child_state_str not in explored:
                # Se não está na fronteira, adicionar
                if child_state_str not in frontier_dict:
                    heapq.heappush(frontier, (child.path_cost, counter, child))
                    frontier_dict[child_state_str] = child
                    counter += 1
                # Se está na fronteira mas com custo maior, atualizar
                elif child.path_cost < frontier_dict[child_state_str].path_cost:
                    # Atualizar na fronteira
                    frontier_dict[child_state_str] = child
                    heapq.heappush(frontier, (child.path_cost, counter, child))
                    counter += 1
    
    # Falha
    return SearchResult(
        success=False,
        nodes_expanded=nodes_expanded,
        nodes_generated=nodes_generated,
        time_elapsed=time.time() - start_time,
        max_frontier_size=max_frontier_size
    )


# Aliases
bfs = breadth_first_search
dfs = depth_first_search
ucs = uniform_cost_search

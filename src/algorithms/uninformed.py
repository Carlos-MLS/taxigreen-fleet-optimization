"""
Algoritmos de Procura Nao-Informada.

Este modulo implementa os algoritmos classicos de procura em espacos de estados
que nao utilizam informacao heuristica. Estes algoritmos exploram o espaco de
estados de forma sistematica, sem "saber" qual direcao e mais promissora.

Algoritmos implementados:
    - BFS (Breadth-First Search): Explora por niveis de profundidade
    - DFS (Depth-First Search): Explora em profundidade primeiro
    - UCS (Uniform Cost Search): Expande por ordem de custo acumulado

Cada algoritmo tem as suas vantagens e desvantagens em termos de completude,
optimalidade e complexidade de memoria.

Autores: Grupo 18 - Inteligencia Artificial 2024/2025
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
    
    O BFS e um dos algoritmos de procura mais fundamentais. Explora o espaco
    de estados "por camadas", visitando todos os nos a uma determinada
    profundidade antes de avancar para a profundidade seguinte.
    
    Funcionamento:
        - Usa uma fila FIFO (First-In-First-Out) como fronteira
        - O primeiro no a entrar na fila e o primeiro a ser explorado
        - Garante encontrar o caminho mais curto em numero de passos
    
    Propriedades:
        - Completo: Sim, encontra solucao se existir (espaco finito)
        - Otimo: Sim, para custos uniformes (todos os passos custam igual)
        - Complexidade temporal: O(b^d) onde b e ramificacao e d profundidade
        - Complexidade espacial: O(b^d) - pode consumir muita memoria!
    
    Exemplo visual (ordem de exploracao):
              1
            / | \\
           2  3  4      <- Nivel 1: explora 2, 3, 4
          /|  |  |\\
         5 6  7  8 9    <- Nivel 2: explora 5, 6, 7, 8, 9
    
    Args:
        problem: O problema de procura a resolver
        max_nodes: Limite de seguranca para evitar memoria excessiva
        
    Returns:
        SearchResult contendo o caminho encontrado e metricas da procura
    """
    start_time = time.time()
    
    # Criar o no inicial a partir do estado de partida
    initial_node = Node(state=problem.initial_state())
    
    # Verificar caso trivial: ja estamos no objetivo?
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
    
    # A fronteira e uma fila FIFO (deque e eficiente para isto)
    # Os nos sao adicionados ao fim e removidos do inicio
    frontier = deque([initial_node])
    
    # Conjunto de estados ja visitados para evitar ciclos
    explored: Set[str] = set()
    
    # Variaveis para metricas de desempenho
    nodes_expanded = 0      # Nos completamente processados
    nodes_generated = 1     # Nos criados (inclui inicial)
    max_frontier_size = 1   # Pico de memoria da fronteira
    
    # Ciclo principal: continuar enquanto houver nos por explorar
    while frontier:
        # Registar tamanho maximo (util para analise de memoria)
        max_frontier_size = max(max_frontier_size, len(frontier))
        
        # Mecanismo de seguranca contra explosao de memoria
        if nodes_expanded >= max_nodes:
            print(f"[AVISO] BFS: Limite de {max_nodes} nos atingido")
            break
        
        # Remover o proximo no da fronteira (FIFO: primeiro a entrar)
        node = frontier.popleft()
        
        # Marcar como explorado
        explored.add(str(node.state))
        nodes_expanded += 1
        
        # Gerar todos os nos filhos (expansao)
        for action in problem.actions(node.state):
            # Aplicar a acao para obter o novo estado
            child_state = problem.result(node.state, action)
            
            # Calcular o custo acumulado ate este filho
            child_cost = problem.path_cost(node.path_cost, node.state, action, child_state)
            
            # Criar o no filho
            child = Node(
                state=child_state,
                parent=node,
                action=action,
                path_cost=child_cost,
                depth=node.depth + 1
            )
            
            nodes_generated += 1
            
            # So considerar estados novos (nao explorados nem na fronteira)
            if str(child.state) not in explored and child not in frontier:
                # Teste de objetivo no momento da geracao (otimizacao do BFS)
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
    
    O DFS explora cada ramo da arvore de procura ate a sua maxima profundidade
    antes de retroceder (backtracking) e explorar outros ramos. E como seguir
    um labirinto mantendo sempre a mao na parede esquerda.
    
    Funcionamento:
        - Usa uma pilha LIFO (Last-In-First-Out) como fronteira
        - O ultimo no adicionado e o primeiro a ser explorado
        - Vai "fundo" antes de ir "largo"
    
    Propriedades:
        - Completo: Nao! Pode ficar preso em ramos infinitos
        - Otimo: Nao! Pode encontrar solucao subotima antes da otima
        - Complexidade temporal: O(b^m) onde m e profundidade maxima
        - Complexidade espacial: O(bm) - vantagem principal! Usa pouca memoria
    
    Exemplo visual (ordem de exploracao com profundidade primeiro):
              1
            / | \\
           2  6  7      <- Explora 2 primeiro, vai fundo...
          /|     |\\
         3 4     8 9    <- ...depois 3, 4, volta, explora 6, 7...
         |
         5              <- ...e finalmente os mais profundos
    
    Quando usar:
        - Problemas com muitas solucoes (encontra uma rapidamente)
        - Quando a memoria e limitada
        - Quando sabemos que a solucao esta "fundo" na arvore
    
    Args:
        problem: O problema de procura a resolver
        max_depth: Limite de profundidade (previne loops infinitos)
        max_nodes: Limite de nos a expandir
        
    Returns:
        SearchResult contendo o caminho encontrado e metricas da procura
    """
    start_time = time.time()
    
    # Criar o no inicial
    initial_node = Node(state=problem.initial_state())
    
    # Verificar caso trivial
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
    
    # A fronteira e uma pilha LIFO (lista Python funciona bem para isto)
    # Os nos sao adicionados e removidos do fim
    frontier = [initial_node]
    
    # Conjunto de estados ja visitados
    explored: Set[str] = set()
    
    # Metricas de desempenho
    nodes_expanded = 0
    nodes_generated = 1
    max_frontier_size = 1
    
    # Ciclo principal
    while frontier:
        max_frontier_size = max(max_frontier_size, len(frontier))
        
        if nodes_expanded >= max_nodes:
            print(f"[AVISO] DFS: Limite de {max_nodes} nos atingido")
            break
        
        # Remover o ultimo no (LIFO: ultimo a entrar, primeiro a sair)
        node = frontier.pop()
        
        # Limite de profundidade: evita explorar demasiado fundo
        # Isto e importante para prevenir loops infinitos
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
    
    O UCS e uma generalizacao do BFS que funciona corretamente quando os
    custos das acoes sao diferentes. Em vez de expandir por ordem de profundidade,
    expande por ordem de custo acumulado.
    
    Funcionamento:
        - Usa uma fila de prioridade ordenada por g(n) (custo do caminho)
        - Expande sempre o no com menor custo acumulado desde o inicio
        - O teste de objetivo e feito quando o no e expandido, nao quando e gerado
    
    Propriedades:
        - Completo: Sim, se os custos forem positivos
        - Otimo: Sim! Garante encontrar o caminho de menor custo
        - Complexidade: O(b^(1+C*/epsilon)) onde C* e custo otimo, epsilon e custo minimo
        - E equivalente ao algoritmo de Dijkstra para grafos
    
    Diferenca para o BFS:
        - BFS encontra o caminho com menos passos
        - UCS encontra o caminho com menor custo total
    
    Exemplo: Se ir de A a B custa 1 ou 10 dependendo da rota,
             o BFS pode encontrar a rota de 10 (se tiver menos passos),
             mas o UCS encontrara sempre a rota de custo 1.
    
    Quando usar:
        - Quando os custos das acoes sao diferentes
        - Quando precisamos do caminho de menor custo (nao apenas mais curto)
        - Problemas de rotas com distancias/tempos variaveis
    
    Args:
        problem: O problema de procura a resolver
        max_nodes: Limite de seguranca
        
    Returns:
        SearchResult contendo o caminho de menor custo e metricas
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
            print(f"[AVISO] UCS: Limite de {max_nodes} nos atingido")
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

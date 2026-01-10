"""
Algoritmos de Procura Informada (Heuristica).

Este modulo implementa os algoritmos de procura que utilizam informacao
heuristica para guiar a exploracao do espaco de estados. Estes algoritmos
sao geralmente mais eficientes que os algoritmos nao-informados porque
conseguem "estimar" a direcao mais promissora para encontrar a solucao.

Algoritmos implementados:
    - A* Search: Combina custo real g(n) com heuristica h(n) para garantir
                 optimalidade quando h(n) e admissivel
    - Greedy Best-First: Usa apenas h(n), sendo rapido mas nao optimo

Autores: Grupo 18 - Inteligencia Artificial 2024/2025
"""

import heapq
from typing import Set, Callable, Optional
import time

from ..utils.node import Node, SearchResult
from ..utils.problem import Problem


def a_star_search(problem: Problem, heuristic: Optional[Callable] = None, max_nodes: int = 100000) -> SearchResult:
    """
    Algoritmo A* (A-estrela) para procura de caminho otimo.
    
    O A* e considerado um dos algoritmos de procura mais importantes em IA.
    Combina as melhores caracteristicas da procura de custo uniforme (UCS)
    com a eficiencia das heuristicas.
    
    Funcionamento:
        - Mantem uma fronteira de nos ordenada por f(n) = g(n) + h(n)
        - g(n): custo real do caminho desde o inicio ate ao no n
        - h(n): estimativa heuristica do custo de n ate ao objetivo
        - Expande sempre o no com menor f(n)
    
    Propriedades:
        - Completo: Sim, encontra solucao se existir
        - Otimo: Sim, se h(n) for admissivel (nunca sobrestima)
        - Complexidade temporal: O(b^d) onde b e ramificacao, d e profundidade
        - Complexidade espacial: O(b^d) - mantem todos os nos em memoria
    
    Args:
        problem: O problema de procura a resolver, com estado inicial e objetivo
        heuristic: Funcao heuristica h(estado) -> float. Se None, usa problem.heuristic
        max_nodes: Limite de seguranca para evitar loops infinitos
        
    Returns:
        SearchResult contendo o caminho encontrado e metricas da procura
    """
    start_time = time.time()
    
    # Se nao foi fornecida uma heuristica especifica, usamos a do problema
    if heuristic is None:
        heuristic = problem.heuristic
    
    # Criamos o no inicial com o estado de partida
    # A heuristica e calculada imediatamente para o primeiro no
    initial_node = Node(
        state=problem.initial_state(),
        heuristic=heuristic(problem.initial_state())
    )
    
    # Caso especial: verificar se ja estamos no objetivo
    # Isto evita trabalho desnecessario em problemas triviais
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
    
    # A fronteira e implementada como uma fila de prioridade (min-heap)
    # Cada elemento e um tuplo (f_score, contador, no) para ordenacao correta
    # O contador serve como desempate quando dois nos tem o mesmo f_score
    frontier = [(initial_node.f_score(), 0, initial_node)]
    
    # Dicionario auxiliar para acesso rapido aos nos na fronteira
    # Permite verificar se um estado ja esta na fronteira em O(1)
    frontier_dict = {str(initial_node.state): initial_node}
    
    # Conjunto de estados ja explorados (visitados e expandidos)
    # Evita re-explorar estados ja processados
    explored: Set[str] = set()
    
    # Variaveis para recolha de metricas de desempenho
    nodes_expanded = 0      # Quantos nos foram completamente processados
    nodes_generated = 1     # Quantos nos foram criados (inclui o inicial)
    max_frontier_size = 1   # Tamanho maximo da fronteira (para analise de memoria)
    counter = 1             # Contador para desempate na fila de prioridade
    
    # Ciclo principal: continua enquanto houver nos por explorar
    # Ciclo principal: continua enquanto houver nos por explorar
    while frontier:
        # Registar o tamanho maximo da fronteira (util para analise)
        max_frontier_size = max(max_frontier_size, len(frontier))
        
        # Mecanismo de seguranca: evitar que o algoritmo corra indefinidamente
        # em problemas muito grandes ou com ciclos
        if nodes_expanded >= max_nodes:
            print(f"[AVISO] A*: Limite de {max_nodes} nos atingido")
            break
        
        # Extrair o no com menor f(n) da fronteira
        # O heapq garante que obtemos sempre o minimo em O(log n)
        _, _, node = heapq.heappop(frontier)
        
        # Remover do dicionario de fronteira para manter consistencia
        state_str = str(node.state)
        if state_str in frontier_dict:
            del frontier_dict[state_str]
        
        # Verificar se este no e o objetivo
        # Se sim, encontramos a solucao otima!
        if problem.goal_test(node.state):
            return SearchResult(
                success=True,
                path=node.get_path(),           # Caminho completo desde o inicio
                solution=node.get_solution(),    # Sequencia de acoes
                cost=node.path_cost,            # Custo total do caminho
                nodes_expanded=nodes_expanded,
                nodes_generated=nodes_generated,
                time_elapsed=time.time() - start_time,
                max_frontier_size=max_frontier_size
            )
        
        # Marcar este estado como explorado para nao o visitar novamente
        explored.add(state_str)
        nodes_expanded += 1
        
        # Expandir o no: gerar todos os estados filhos possiveis
        for action in problem.actions(node.state):
            # Aplicar a acao para obter o novo estado
            child_state = problem.result(node.state, action)
            child_state_str = str(child_state)
            
            # Calcular o custo do caminho ate este filho
            # g(filho) = g(pai) + custo(pai, acao, filho)
            child_cost = problem.path_cost(node.path_cost, node.state, action, child_state)
            
            # Criar o no filho com todas as informacoes necessarias
            child = Node(
                state=child_state,
                parent=node,            # Ligacao ao pai para reconstruir caminho
                action=action,          # Acao que levou a este estado
                path_cost=child_cost,   # Custo acumulado g(n)
                depth=node.depth + 1,   # Profundidade na arvore de procura
                heuristic=heuristic(child_state)  # Estimativa h(n)
            )
            
            nodes_generated += 1
            
            # So consideramos este filho se ainda nao foi explorado
            if child_state_str not in explored:
                # Caso 1: Estado novo - adicionar a fronteira
                if child_state_str not in frontier_dict:
                    heapq.heappush(frontier, (child.f_score(), counter, child))
                    frontier_dict[child_state_str] = child
                    counter += 1
                # Caso 2: Estado ja na fronteira mas com custo maior
                # Substituir pelo caminho mais barato (atualizacao de prioridade)
                elif child.f_score() < frontier_dict[child_state_str].f_score():
                    frontier_dict[child_state_str] = child
                    heapq.heappush(frontier, (child.f_score(), counter, child))
                    counter += 1
    
    # Se chegamos aqui, a fronteira esvaziou sem encontrar solucao
    return SearchResult(
        success=False,
        nodes_expanded=nodes_expanded,
        nodes_generated=nodes_generated,
        time_elapsed=time.time() - start_time,
        max_frontier_size=max_frontier_size
    )


def greedy_best_first_search(problem: Problem, heuristic: Optional[Callable] = None, max_nodes: int = 100000) -> SearchResult:
    """
    Greedy Best-First Search (Procura Gulosa pelo Melhor Primeiro).
    
    Este algoritmo e "guloso" porque toma sempre a decisao que parece melhor
    no momento, sem considerar o custo ja gasto. E como escolher sempre o
    caminho que parece mais curto sem olhar para tras.
    
    Funcionamento:
        - Ordena a fronteira apenas por h(n), ignorando g(n)
        - Expande sempre o no que parece estar mais proximo do objetivo
        - Pode encontrar solucoes muito rapidamente, mas sem garantia de otimalidade
    
    Propriedades:
        - Completo: Nao, pode ficar preso em ciclos ou ramos infinitos
        - Otimo: Nao, ignora o custo do caminho percorrido
        - Vantagem: Pode ser muito mais rapido que A* em certos problemas
        - Desvantagem: A solucao encontrada pode nao ser a melhor
    
    Quando usar:
        - Quando precisamos de uma solucao rapida e nao necessariamente otima
        - Quando a heuristica e muito boa e confiavel
        - Em problemas onde a exploracao completa e inviavel
    
    Args:
        problem: O problema de procura a resolver
        heuristic: Funcao heuristica h(estado) -> float
        max_nodes: Limite de seguranca para evitar loops infinitos
        
    Returns:
        SearchResult contendo o caminho encontrado e metricas da procura
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
            print(f"[AVISO] Greedy: Limite de {max_nodes} nos atingido")
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


# Aliases
astar = a_star_search
greedy = greedy_best_first_search

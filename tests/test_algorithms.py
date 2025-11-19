"""
Testes para algoritmos de procura.
Valida implementações de BFS, DFS, UCS, A*, Greedy.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.models.city import City
from src.utils.problem import RouteProblem
from src.algorithms import (
    breadth_first_search,
    depth_first_search,
    uniform_cost_search,
    a_star_search,
    greedy_best_first_search,
    heuristic_euclidean,
    HeuristicFactory
)


def criar_cidade_teste() -> City:
    """Cria uma cidade simples para testes."""
    cidade = City()
    
    # Adicionar nós com coordenadas
    coordenadas = {
        'A': (0, 0),
        'B': (1, 0),
        'C': (2, 0),
        'D': (0, 1),
        'E': (1, 1),
        'F': (2, 1),
        'G': (0, 2),
        'H': (1, 2),
        'I': (2, 2)
    }
    
    cidade.coordenadas = coordenadas
    
    # Criar grafo em grelha 3x3
    # A-B-C
    # D-E-F
    # G-H-I
    
    # Linha superior
    cidade.adicionar_aresta('A', 'B', 1.0, 2.0)
    cidade.adicionar_aresta('B', 'C', 1.0, 2.0)
    
    # Linha média
    cidade.adicionar_aresta('D', 'E', 1.0, 2.0)
    cidade.adicionar_aresta('E', 'F', 1.0, 2.0)
    
    # Linha inferior
    cidade.adicionar_aresta('G', 'H', 1.0, 2.0)
    cidade.adicionar_aresta('H', 'I', 1.0, 2.0)
    
    # Colunas
    cidade.adicionar_aresta('A', 'D', 1.0, 2.0)
    cidade.adicionar_aresta('D', 'G', 1.0, 2.0)
    
    cidade.adicionar_aresta('B', 'E', 1.0, 2.0)
    cidade.adicionar_aresta('E', 'H', 1.0, 2.0)
    
    cidade.adicionar_aresta('C', 'F', 1.0, 2.0)
    cidade.adicionar_aresta('F', 'I', 1.0, 2.0)
    
    # Diagonais (opcionais)
    cidade.adicionar_aresta('A', 'E', 1.414, 3.0)
    cidade.adicionar_aresta('E', 'I', 1.414, 3.0)
    
    return cidade


def testar_bfs():
    """Testa Breadth-First Search."""
    print("\n=== TESTE: BFS ===")
    
    cidade = criar_cidade_teste()
    problema = RouteProblem(cidade, 'A', 'I')
    
    resultado = breadth_first_search(problema)
    
    print(f"Sucesso: {resultado.success}")
    print(f"Caminho (estados): {[n.state for n in resultado.path]}")
    print(f"Solução (ações): {resultado.solution}")
    print(f"Custo: {resultado.cost:.2f}")
    print(f"Nós expandidos: {resultado.nodes_expanded}")
    print(f"Nós gerados: {resultado.nodes_generated}")
    print(f"Tempo: {resultado.time_elapsed:.4f}s")
    print(f"Máx fronteira: {resultado.max_frontier_size}")
    
    # Validações
    assert resultado.success, "BFS deveria encontrar solução"
    assert resultado.path[0].state == 'A', "Deve começar em A"
    assert resultado.path[-1].state == 'I', "Deve terminar em I"
    
    print("✓ BFS passou em todos os testes")


def testar_dfs():
    """Testa Depth-First Search."""
    print("\n=== TESTE: DFS ===")
    
    cidade = criar_cidade_teste()
    problema = RouteProblem(cidade, 'A', 'I')
    
    resultado = depth_first_search(problema, max_depth=10)
    
    print(f"Sucesso: {resultado.success}")
    print(f"Caminho (estados): {[n.state for n in resultado.path]}")
    print(f"Custo: {resultado.cost:.2f}")
    print(f"Nós expandidos: {resultado.nodes_expanded}")
    
    # Validações
    assert resultado.success, "DFS deveria encontrar solução"
    assert resultado.path[0].state == 'A', "Deve começar em A"
    assert resultado.path[-1].state == 'I', "Deve terminar em I"
    
    print("✓ DFS passou em todos os testes")


def testar_ucs():
    """Testa Uniform Cost Search."""
    print("\n=== TESTE: UCS ===")
    
    cidade = criar_cidade_teste()
    problema = RouteProblem(cidade, 'A', 'I')
    
    resultado = uniform_cost_search(problema)
    
    print(f"Sucesso: {resultado.success}")
    print(f"Caminho (estados): {[n.state for n in resultado.path]}")
    print(f"Custo: {resultado.cost:.2f}")
    print(f"Nós expandidos: {resultado.nodes_expanded}")
    
    # Validações
    assert resultado.success, "UCS deveria encontrar solução"
    assert resultado.path[0].state == 'A', "Deve começar em A"
    assert resultado.path[-1].state == 'I', "Deve terminar em I"
    
    print("✓ UCS passou em todos os testes")


def testar_a_star():
    """Testa A* Search."""
    print("\n=== TESTE: A* ===")
    
    cidade = criar_cidade_teste()
    problema = RouteProblem(cidade, 'A', 'I')
    
    # Criar heurística
    heuristic = HeuristicFactory.create_euclidean(cidade.coordenadas, 'I')
    
    resultado = a_star_search(problema, heuristic)
    
    print(f"Sucesso: {resultado.success}")
    print(f"Caminho (estados): {[n.state for n in resultado.path]}")
    print(f"Custo: {resultado.cost:.2f}")
    print(f"Nós expandidos: {resultado.nodes_expanded}")
    print(f"Tempo: {resultado.time_elapsed:.4f}s")
    
    # Validações
    assert resultado.success, "A* deveria encontrar solução"
    assert resultado.path[0].state == 'A', "Deve começar em A"
    assert resultado.path[-1].state == 'I', "Deve terminar em I"
    
    print("✓ A* passou em todos os testes")


def testar_greedy():
    """Testa Greedy Best-First Search."""
    print("\n=== TESTE: Greedy ===")
    
    cidade = criar_cidade_teste()
    problema = RouteProblem(cidade, 'A', 'I')
    
    # Criar heurística
    heuristic = HeuristicFactory.create_euclidean(cidade.coordenadas, 'I')
    
    resultado = greedy_best_first_search(problema, heuristic)
    
    print(f"Sucesso: {resultado.success}")
    print(f"Caminho (estados): {[n.state for n in resultado.path]}")
    print(f"Custo: {resultado.cost:.2f}")
    print(f"Nós expandidos: {resultado.nodes_expanded}")
    
    # Validações
    assert resultado.success, "Greedy deveria encontrar solução"
    assert resultado.path[0].state == 'A', "Deve começar em A"
    assert resultado.path[-1].state == 'I', "Deve terminar em I"
    
    print("✓ Greedy passou em todos os testes")


def comparar_algoritmos():
    """Compara desempenho de todos os algoritmos."""
    print("\n=== COMPARAÇÃO DE ALGORITMOS ===")
    
    cidade = criar_cidade_teste()
    problema = RouteProblem(cidade, 'A', 'I')
    
    # Criar heurística para algoritmos informados
    heuristic = HeuristicFactory.create_euclidean(cidade.coordenadas, 'I')
    
    # Executar todos os algoritmos
    algoritmos = {
        'BFS': lambda: breadth_first_search(problema),
        'DFS': lambda: depth_first_search(problema, max_depth=10),
        'UCS': lambda: uniform_cost_search(problema),
        'A*': lambda: a_star_search(problema, heuristic),
        'Greedy': lambda: greedy_best_first_search(problema, heuristic)
    }
    
    resultados = {}
    for nome, func in algoritmos.items():
        resultado = func()
        resultados[nome] = resultado
    
    # Tabela de comparação
    print(f"\n{'Algoritmo':<10} {'Custo':<10} {'Nós Exp.':<12} {'Nós Ger.':<12} {'Tempo (s)':<12}")
    print("-" * 66)
    
    for nome, res in resultados.items():
        print(f"{nome:<10} {res.cost:<10.2f} {res.nodes_expanded:<12} "
              f"{res.nodes_generated:<12} {res.time_elapsed:<12.6f}")
    
    # Encontrar melhor em cada métrica
    print("\n=== MELHORES ===")
    
    melhor_custo = min(resultados.items(), key=lambda x: x[1].cost)
    print(f"Menor custo: {melhor_custo[0]} ({melhor_custo[1].cost:.2f})")
    
    melhor_nos = min(resultados.items(), key=lambda x: x[1].nodes_expanded)
    print(f"Menos nós expandidos: {melhor_nos[0]} ({melhor_nos[1].nodes_expanded})")
    
    melhor_tempo = min(resultados.items(), key=lambda x: x[1].time_elapsed)
    print(f"Mais rápido: {melhor_tempo[0]} ({melhor_tempo[1].time_elapsed:.6f}s)")


def testar_caminho_bloqueado():
    """Testa algoritmos com estrada bloqueada."""
    print("\n=== TESTE: Caminho Bloqueado ===")
    
    cidade = criar_cidade_teste()
    
    # Bloquear caminho direto A->E->I
    cidade.cortar_estrada('A', 'E', 60.0)  # Bloquear por 60 minutos
    cidade.cortar_estrada('E', 'I', 60.0)
    
    problema = RouteProblem(cidade, 'A', 'I')
    heuristic = HeuristicFactory.create_euclidean(cidade.coordenadas, 'I')
    
    # Testar A*
    resultado = a_star_search(problema, heuristic)
    
    caminho_estados = [n.state for n in resultado.path]
    print(f"Caminho com bloqueios: {caminho_estados}")
    print(f"Custo: {resultado.cost:.2f}")
    
    # Verificar que não usa arestas bloqueadas
    assert 'E' not in caminho_estados or (
        (caminho_estados.index('A') + 1 != caminho_estados.index('E') if 'E' in caminho_estados else True)
    ), "Não deve usar aresta bloqueada A-E"
    
    print("✓ Teste de bloqueio passou")


def main():
    """Executa todos os testes."""
    print("=" * 70)
    print(" TESTES DE ALGORITMOS DE PROCURA ".center(70))
    print("=" * 70)
    
    try:
        testar_bfs()
        testar_dfs()
        testar_ucs()
        testar_a_star()
        testar_greedy()
        comparar_algoritmos()
        testar_caminho_bloqueado()
        
        print("\n" + "=" * 70)
        print(" ✓ TODOS OS TESTES PASSARAM ".center(70, '='))
        print("=" * 70)
        
    except AssertionError as e:
        print(f"\n✗ TESTE FALHOU: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ ERRO: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())

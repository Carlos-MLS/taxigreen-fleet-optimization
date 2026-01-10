# Manual de Utilizacao - TaxiGreen

## Requisitos

- Python 3.8+
- Bibliotecas: nenhuma externa necessaria (apenas stdlib)

## Estrutura do Projeto

```
src/
    algorithms/     - Algoritmos de procura (BFS, DFS, A*, IDA*, etc.)
    allocation/     - Estrategias de alocacao de veiculos
    models/         - Modelos de dados (Veiculo, Pedido, Cidade)
    simulation/     - Simulador de eventos
    utils/          - Metricas e utilitarios
tests/              - Testes unitarios e de integracao
config.py           - Configuracoes do sistema
main.py             - Ponto de entrada principal
gerar_resultados.py - Geracao de resultados experimentais
```

## Execucao

### Demonstracao basica
```bash
python3 demo_simple.py
```

### Geracao de resultados experimentais
```bash
python3 gerar_resultados.py
```
Resultados exportados para `resultados/resultados_YYYYMMDD_HHMMSS.json`

### Testes
```bash
# Testes unitarios de algoritmos
python3 -m pytest tests/test_algorithms.py -v

# Testes de integracao
python3 tests/test_integration.py
```

## Configuracao

Editar `config.py` para ajustar:
- Velocidade media dos veiculos
- Custos por tipo de veiculo
- Fatores de emissao CO2
- Penalidades e pesos de estrategias

## Algoritmos Disponiveis

| Codigo | Algoritmo |
|--------|-----------|
| bfs | Breadth-First Search |
| dfs | Depth-First Search |
| ucs | Uniform Cost Search |
| ids | Iterative Deepening Search |
| astar | A* Search |
| greedy | Greedy Best-First Search |
| weighted_astar | Weighted A* |
| idastar | IDA* |

## Estrategias de Alocacao

| Codigo | Estrategia |
|--------|------------|
| nearest | Veiculo mais proximo |
| lowest_cost | Menor custo operacional |
| eco_friendly | Menor impacto ambiental |
| min_emissions | Minimizar emissoes |
| balanced | Equilibrio custo-tempo |
| priority_aware | Prioridade do pedido |

## Metricas Calculadas

1. Tempo medio de resposta (minutos)
2. Taxa de ocupacao da frota (%)
3. Custos operacionais totais (EUR)
4. Emissoes de CO2 (kg)
5. Pedidos nao atendidos
6. Km percorridos vazios

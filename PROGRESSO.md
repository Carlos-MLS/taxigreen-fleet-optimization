# Estado do Trabalho - TaxiGreen

**Data:** 5 de novembro de 2025  
**Prazo de Entrega:** 21 de dezembro de 2025

---

## ✅ TAREFAS CONCLUÍDAS

### 1. Documentação e Formulação
- ✅ **REQUISITOS.md** - Análise completa dos requisitos (13 secções)
- ✅ **RELATORIO.md** - Formulação académica do problema
  - Problema formulado como **Contingency Problem**
  - Representação de estado: S = (V, P, C, T)
  - 8 operadores definidos com pré-condições, efeitos e custos
  - Função de custo multi-objetivo com 6 componentes ponderadas

### 2. Modelo de Dados (Base Classes)
- ✅ **Vehicle** (`src/models/vehicle.py`) - Veículos elétricos/combustão
  - Tipos de motorização, autonomia, capacidade
  - Métodos: aceitar_pedido, consumir_autonomia, calcular_emissoes
  - Estados: disponível, ocupado, em_recarga, em_manutencao
  
- ✅ **Request** (`src/models/request.py`) - Pedidos de transporte
  - Prioridades (normal, urgente, premium)
  - Preferências ambientais
  - Métodos: atribuir_veiculo, tempo_resposta, peso_prioridade
  
- ✅ **Station** (`src/models/station.py`) - Estações de recarga/abastecimento
  - Tipos: recarga_rapida, recarga_normal, abastecimento
  - Capacidade e disponibilidade
  - Métodos: aceitar_veiculo, libertar_veiculo, avariar
  
- ✅ **City** (`src/models/city.py`) - Grafo da cidade
  - Nós e arestas dinâmicas
  - Fatores de trânsito (1.0 - 3.0x)
  - Estradas bloqueadas com duração
  - Métodos: adicionar_aresta, cortar_estrada, atualizar_transito

### 3. Sistema de Configuração
- ✅ **config.py** - Parâmetros globais
  - Configurações de veículos (autonomia, capacidade, emissões)
  - Padrões de trânsito por hora do dia
  - Pesos da função de custo (α₁=0.30, α₂=0.25, ...)
  - Probabilidades de eventos (avarias, bloqueios)

### 4. Infraestrutura de Procura
- ✅ **Node** (`src/utils/node.py`) - Nó da árvore de procura
  - Armazenamento: state, parent, action, path_cost, depth, heuristic
  - Métodos: get_path(), get_solution(), f_score()
  - SearchResult com 8 métricas

- ✅ **Problem** (`src/utils/problem.py`) - Classe abstrata de problemas
  - Métodos abstratos: initial_state, goal_test, actions, result, step_cost, heuristic
  - RouteProblem para navegação em grafos

### 5. Algoritmos de Procura ⭐
- ✅ **BFS** - Breadth-First Search (completo, ótimo para custos uniformes)
- ✅ **DFS** - Depth-First Search (com limite de profundidade)
- ✅ **UCS** - Uniform Cost Search (completo, ótimo)
- ✅ **A*** - A-Star (ótimo com heurística admissível)
- ✅ **Greedy** - Gulosa (rápida, não ótima)
- ✅ **Weighted A*** - A* ponderado (trade-off velocidade/qualidade)

### 6. Heurísticas (`src/algorithms/heuristics.py`)
- ✅ **Euclidiana** - Distância em linha reta
- ✅ **Manhattan** - Soma de diferenças absolutas
- ✅ **Chebyshev** - Máximo das diferenças
- ✅ **Haversine** - Grande círculo (GPS)
- ✅ **Time Estimate** - Tempo baseado em velocidade média
- ✅ **Composite** - Com fator de trânsito
- ✅ **Min Stations** - Considerando recargas necessárias
- ✅ **HeuristicFactory** - Factory para criar heurísticas configuradas
- ✅ Funções de validação: is_admissible(), is_consistent()

### 7. Testes
- ✅ **test_models.py** - Testes unitários das classes base (100% passing)
- ✅ **test_algorithms.py** - Testes de algoritmos de procura (100% passing)
  - Teste de todos os algoritmos (BFS, DFS, UCS, A*, Greedy)
  - Comparação de performance
  - Teste com caminhos bloqueados
  - Métricas: custo, nós expandidos, tempo de execução

### 8. Programa Principal
- ✅ **main.py** - Demonstração básica do sistema
- ✅ **README.md** - Documentação completa do projeto

---

## ❌ TAREFAS PENDENTES (CRÍTICAS)

### 1. Problema Específico dos Táxis 🔴 PRIORITÁRIO
**Falta:** Criar `TaxiProblem` que estenda a classe `Problem` para modelar alocação de veículos

**O que implementar:**
```python
# src/utils/taxi_problem.py
class TaxiProblem(Problem):
    """
    Problema de alocação e roteamento de táxis.
    
    Estado: (veículos_posições, veículos_autonomia, pedidos_pendentes, tempo_atual)
    """
    
    def __init__(self, frota, pedidos, cidade, config):
        # Inicializar com frota, pedidos e cidade
        
    def initial_state(self):
        # Estado inicial: posições dos veículos, pedidos pendentes
        
    def goal_test(self, state):
        # Todos os pedidos atendidos ou justificadamente rejeitados
        
    def actions(self, state):
        # Ações: alocar, deslocar, recarregar, rejeitar
        
    def result(self, state, action):
        # Novo estado após aplicar ação
        
    def step_cost(self, state, action, next_state):
        # Custo multiobjetivo (tempo, distância, emissões, etc.)
        
    def heuristic(self, state):
        # Estimativa do custo para completar todos os pedidos
```

**Complexidade:** Alta  
**Tempo estimado:** 4-6 horas

### 2. Sistema de Simulação Dinâmica 🔴 PRIORITÁRIO
**Falta:** Motor de simulação que processa eventos ao longo do tempo

**O que implementar:**
```python
# src/simulation/simulator.py
class TaxiSimulator:
    """
    Simula operação da frota ao longo do tempo.
    
    - Chegada dinâmica de pedidos
    - Atualização de autonomia dos veículos
    - Eventos aleatórios (trânsito, avarias)
    - Recargas e reabastecimentos
    """
    
    def __init__(self, cidade, frota, config):
        self.cidade = cidade
        self.frota = frota
        self.tempo_atual = 0
        self.eventos = []
        self.metricas = MetricsCollector()
    
    def adicionar_pedido(self, pedido):
        # Adiciona pedido à fila
        
    def step(self, delta_tempo):
        # Avança simulação por delta_tempo
        # - Processa eventos pendentes
        # - Atualiza estados dos veículos
        # - Atualiza trânsito
        # - Gera eventos aleatórios
        
    def executar_ate(self, tempo_final):
        # Simula até tempo_final
        
    def obter_metricas(self):
        # Retorna métricas acumuladas
```

**Complexidade:** Alta  
**Tempo estimado:** 5-7 horas

### 3. Sistema de Métricas 🟡 IMPORTANTE
**Falta:** Coletor de métricas para avaliação

**O que implementar:**
```python
# src/simulation/metrics.py
class MetricsCollector:
    """
    Coleta e calcula métricas de desempenho.
    
    Métricas obrigatórias:
    1. Tempo médio de resposta ao pedido
    2. Taxa de ocupação da frota
    3. Custos operacionais totais
    4. Emissões de CO2 estimadas
    5. Número de pedidos não atendidos/rejeitados
    6. Km percorridos sem passageiros
    """
    
    def __init__(self):
        self.pedidos_atendidos = []
        self.pedidos_rejeitados = []
        self.km_vazios = 0
        self.custo_total = 0
        self.emissoes_total = 0
        # ...
    
    def registrar_pedido_atendido(self, pedido, tempo_resposta):
        # Registra pedido atendido
        
    def calcular_tempo_medio_resposta(self):
        # Retorna média
        
    def calcular_taxa_ocupacao(self):
        # % do tempo que veículos estão ocupados
        
    # ... outros cálculos
    
    def gerar_relatorio(self):
        # Relatório completo em formato dict/JSON
```

**Complexidade:** Média  
**Tempo estimado:** 2-3 horas

### 4. Estratégias de Alocação 🟡 IMPORTANTE
**Falta:** Implementar diferentes estratégias de decisão

**O que implementar:**
```python
# src/strategies/allocation.py
class AllocationStrategy(ABC):
    """Estratégia base de alocação."""
    
    @abstractmethod
    def alocar_veiculo(self, pedido, frota, cidade):
        pass

class NearestVehicleStrategy(AllocationStrategy):
    """Aloca veículo mais próximo disponível."""
    
class LowestCostStrategy(AllocationStrategy):
    """Aloca veículo com menor custo operacional."""
    
class EcoFriendlyStrategy(AllocationStrategy):
    """Prioriza veículos elétricos quando possível."""
    
class OptimalSearchStrategy(AllocationStrategy):
    """Usa A* para encontrar melhor alocação."""
    
    def __init__(self, search_algorithm='a_star'):
        self.algorithm = search_algorithm
```

**Complexidade:** Média  
**Tempo estimado:** 3-4 horas

### 5. Integração e Testes de Sistema 🟡 IMPORTANTE
**Falta:** Testar sistema completo com casos reais

**O que implementar:**
```python
# tests/test_integration.py
def test_simulation_completa():
    """Testa simulação de 1 dia completo."""
    
def test_comparacao_estrategias():
    """Compara diferentes estratégias de alocação."""
    
def test_cenarios_extremos():
    """Testa alta demanda, baixa autonomia, etc."""
    
# scenarios/
# - scenario_rush_hour.py
# - scenario_low_battery.py
# - scenario_station_failure.py
```

**Complexidade:** Média  
**Tempo estimado:** 3-4 horas

### 6. Visualizações e Demonstrações 🟢 DESEJÁVEL
**Falta:** Ferramentas para visualizar resultados

**O que implementar:**
```python
# src/visualization/plotter.py
class ResultPlotter:
    """Cria gráficos de métricas."""
    
    def plot_tempo_resposta(self, metricas):
        # Gráfico de tempo médio ao longo do dia
        
    def plot_custos(self, metricas):
        # Comparação de custos entre estratégias
        
    def plot_ocupacao(self, metricas):
        # Taxa de ocupação da frota
        
    def plot_mapa_rotas(self, cidade, rotas):
        # Visualiza rotas no mapa
```

**Ferramentas sugeridas:** matplotlib, plotly  
**Complexidade:** Baixa  
**Tempo estimado:** 2-3 horas

---

## 📝 TAREFAS PENDENTES (RELATÓRIO)

### 7. Completar Relatório 🔴 PRIORITÁRIO
**Falta:** Secções do RELATORIO.md

**Secções a completar:**
- ✅ Secção 1: Introdução (feita)
- ✅ Secção 2: Formulação do Problema (feita)
- ❌ **Secção 3: Implementação**
  - Arquitetura do sistema
  - Decisões de design
  - Algoritmos implementados
  - Estruturas de dados utilizadas
  
- ❌ **Secção 4: Resultados Experimentais**
  - Configuração dos experimentos
  - Comparação de algoritmos (tabelas e gráficos)
  - Análise de diferentes cenários
  - Comparação de estratégias de alocação
  
- ❌ **Secção 5: Discussão**
  - Análise crítica dos resultados
  - Limitações do sistema
  - Trade-offs identificados
  - Comparação com literatura
  
- ❌ **Secção 6: Conclusões**
  - Sumário dos resultados
  - Contribuições do trabalho
  - Trabalho futuro

**Complexidade:** Média  
**Tempo estimado:** 4-6 horas (após implementação estar completa)

---

## 🎯 FUNCIONALIDADES EXTRA (OPCIONAL - VALORIZAM)

### 8. Predição de Procura 🌟 EXTRA
- Análise de padrões históricos
- Predição de zonas de alta demanda
- Posicionamento proativo de veículos

### 9. Ride-Sharing 🌟 EXTRA
- Múltiplos passageiros no mesmo veículo
- Otimização de rotas partilhadas

### 10. Integração com Dados Externos 🌟 EXTRA
- Dados meteorológicos (impacto da chuva)
- Tráfego em tempo real
- Eventos especiais (jogos, concertos)

### 11. Otimização de Turnos 🌟 EXTRA
- Distribuição de veículos ao longo do dia
- Gestão de períodos de manutenção

---

## 📊 ESTIMATIVA TOTAL DE TEMPO RESTANTE

### Tarefas Críticas (MUST HAVE):
- TaxiProblem: **4-6h**
- Simulador: **5-7h**
- Métricas: **2-3h**
- Estratégias: **3-4h**
- Testes Integração: **3-4h**
- Relatório: **4-6h**

**TOTAL CRÍTICO: 21-30 horas**

### Tarefas Desejáveis (SHOULD HAVE):
- Visualizações: **2-3h**

### Tarefas Opcionais (NICE TO HAVE):
- Features extra: **5-10h** (se houver tempo)

---

## 🗓️ PLANEAMENTO SUGERIDO

### Semana 1 (5-11 nov):
- [ ] Implementar TaxiProblem (2 dias)
- [ ] Implementar Simulador base (2 dias)
- [ ] Implementar MetricsCollector (1 dia)

### Semana 2 (12-18 nov):
- [ ] Implementar Estratégias de Alocação (2 dias)
- [ ] Testes de Integração (2 dias)
- [ ] Cenários de teste (1 dia)

### Semana 3 (19-25 nov):
- [ ] Executar experimentos (2 dias)
- [ ] Criar visualizações (1 dia)
- [ ] Iniciar Relatório Secção 3 (2 dias)

### Semana 4 (26 nov - 2 dez):
- [ ] Completar Secção 4 do Relatório (2 dias)
- [ ] Completar Secção 5 do Relatório (2 dias)
- [ ] Refinar implementação (1 dia)

### Semana 5 (3-9 dez):
- [ ] Completar Secção 6 do Relatório (1 dia)
- [ ] Revisão geral (2 dias)
- [ ] Features extra se houver tempo (2 dias)

### Semana 6 (10-16 dez):
- [ ] Finalização e testes finais (2 dias)
- [ ] Preparar apresentação (2 dias)
- [ ] Buffer para imprevistos (1 dia)

**Entrega: 21 de dezembro de 2025**  
**Apresentação: 12-16 de janeiro de 2026**

---

## ✅ PRÓXIMOS PASSOS IMEDIATOS

1. **Criar TaxiProblem** - Modelar problema específico dos táxis
2. **Criar Simulador** - Motor de simulação dinâmica
3. **Criar MetricsCollector** - Sistema de métricas
4. **Testar integração** - Validar sistema completo
5. **Gerar resultados** - Executar experimentos
6. **Completar relatório** - Documentar tudo

---

## 📌 NOTAS IMPORTANTES

- **Código já está bem estruturado** ✅
- **Algoritmos de procura funcionam** ✅
- **Falta principalmente:** Lógica de negócio dos táxis e simulação
- **Relatório pode ser escrito em paralelo** com implementação
- **Testes ajudam a validar** cada componente
- **Visualizações são importantes** para apresentação

**Estimativa realista:** Com trabalho consistente, **3-4 semanas** são suficientes para completar tudo com qualidade.

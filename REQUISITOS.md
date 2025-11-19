# Requisitos do Trabalho - Gestão de Frota TaxiGreen

**Disciplina:** Inteligência Artificial  
**Ano Letivo:** 2024/2025  
**Data de Entrega:** 21 de dezembro de 2025 (sem penalização até 9 de janeiro de 2026)  
**Apresentação:** 12-16 de janeiro de 2026

---

## 1. FORMULAÇÃO DO PROBLEMA DE PROCURA

### 1.1 Estado Inicial
- **Frota de veículos** com características:
  - Tipo de motorização (combustão/elétrico)
  - Autonomia atual e máxima
  - Capacidade de passageiros
  - Custo operacional por km
  - Localização atual
  - Estado de disponibilidade
- **Mapa da cidade** (grafo)
- **Pedidos pendentes** (se existirem)
- **Estações de recarga/abastecimento** com disponibilidade

### 1.2 Teste Objetivo
- Todos os pedidos atendidos ou decisão justificada de rejeição
- Otimização de métricas (custo, tempo, satisfação)
- Respeito às restrições dos veículos (autonomia, capacidade)

### 1.3 Operadores (Ações Disponíveis)
- **Alocar veículo** a um pedido
- **Deslocar veículo** para local de recolha
- **Transportar passageiros** até destino
- **Recarregar/reabastecer** veículo
- **Reposicionar veículo** proativamente
- **Rejeitar pedido** (com justificação)
- **Aguardar** (veículo em standby)

### 1.4 Custo da Solução
Função multiobjetivo considerando:
- Tempo de resposta ao pedido
- Distância percorrida
- Custo operacional (combustível/eletricidade)
- Km percorridos sem passageiros
- Emissões de CO₂
- Penalizações por pedidos rejeitados
- Satisfação do cliente

---

## 2. REPRESENTAÇÃO EM GRAFO

### 2.1 Nós
- **Zonas de recolha de passageiros** (origem de pedidos)
- **Destinos** (locais de entrega)
- **Estações de recarga** (para veículos elétricos)
- **Postos de abastecimento** (para veículos a combustão)
- **Pontos estratégicos** (intersecções, zonas centrais)

### 2.2 Arestas
- **Distância** entre localizações (em km)
- **Tempo de deslocação** (minutos)
- **Custo de percurso**
- **Condições de trânsito** (variável)
- **Estado da estrada** (normal/cortada)

### 2.3 Características da Cidade
- Distribuição geográfica (zonas centrais vs. periféricas)
- Padrões de trânsito ao longo do dia
- Disponibilidade de infraestrutura (recarga/abastecimento)

---

## 3. ALGORITMOS DE PROCURA

### 3.1 Procura Não Informada
Implementar e comparar:
- **BFS** (Breadth-First Search)
- **DFS** (Depth-First Search)
- **Uniform Cost Search**
- **Iterative Deepening**

### 3.2 Procura Informada
Implementar e comparar:
- **Greedy Best-First Search**
- **A*** (A-Star)
- **IDA*** (Iterative Deepening A*)
- Outros algoritmos relevantes

### 3.3 Heurísticas
Desenvolver heurísticas considerando:
- Distância euclidiana/Manhattan até destino
- Autonomia restante do veículo
- Custo operacional estimado
- Tempo de espera do cliente
- Prioridade do pedido
- Preferência ambiental

### 3.4 Critérios de Comparação
- Tempo de execução
- Número de nós expandidos
- Qualidade da solução
- Uso de memória
- Adaptabilidade a condições dinâmicas

---

## 4. SISTEMA DE SIMULAÇÃO DINÂMICA

### 4.1 Geração de Pedidos
- **Chegada aleatória** ao longo do tempo
- **Distribuição temporal** (rush hours, períodos calmos)
- **Distribuição geográfica** (zonas de alta/baixa procura)
- **Características dos pedidos:**
  - Localização de origem
  - Destino
  - Número de passageiros (1-N)
  - Horário pretendido
  - Prioridade (normal/urgente/premium)
  - Preferência ambiental (sim/não/indiferente)
  - Tempo de espera máximo

### 4.2 Gestão da Frota
- **Atualização contínua** de posições
- **Variação de autonomia** durante deslocações
- **Gestão de recargas/reabastecimentos**
- **Tempo de recarga** (elétricos: 30-60min)
- **Tempo de reabastecimento** (combustão: 5-10min)

### 4.3 Condições Dinâmicas (OBRIGATÓRIAS)
- ✅ **Mudanças de trânsito** que afetam tempos de deslocação
- ✅ **Falhas em estações de recarga**
- ✅ **Variação de combustível/autonomia**
- ✅ **Estradas cortadas** por determinado tempo
- Eventos imprevistos (acidentes, obras)
- Disponibilidade variável de estações

### 4.4 Relógio de Simulação
- Tempo discreto ou contínuo
- Janelas temporais para pedidos
- Sincronização de eventos

---

## 5. MÉTRICAS DE AVALIAÇÃO (OBRIGATÓRIAS)

### 5.1 Métricas Quantitativas
✅ **Tempo médio de resposta ao pedido**
- Desde a criação até atribuição de veículo
- Desde atribuição até início do transporte

✅ **Taxa de ocupação da frota**
- % de tempo com passageiros
- % de tempo em deslocação sem passageiros
- % de tempo parado/recarga

✅ **Custos operacionais totais**
- Custo total por km
- Custo por tipo de veículo
- Custo de combustível/eletricidade
- Custo por pedido atendido

✅ **Emissões de CO₂ estimadas**
- Emissões por veículo a combustão
- Comparação combustão vs. elétrico
- Pegada de carbono total

✅ **Número de pedidos não atendidos/rejeitados**
- Taxa de rejeição
- Motivos de rejeição
- Distribuição temporal/geográfica

✅ **Km percorridos sem passageiros**
- Total de km vazios
- Média por veículo
- % em relação ao total percorrido

### 5.2 Métricas Qualitativas
- Satisfação estimada do cliente
- Equilíbrio de utilização da frota
- Eficiência energética
- Sustentabilidade ambiental

---

## 6. CARACTERÍSTICAS DOS VEÍCULOS

### 6.1 Veículos Elétricos
- **Autonomia:** 150-300 km
- **Capacidade:** 1-4 passageiros
- **Custo/km:** €0.10-€0.15
- **Tempo de recarga:** 30-60 minutos
- **Emissões:** 0 g CO₂/km (localmente)
- **Vantagens:** menor custo, sustentável
- **Desvantagens:** autonomia limitada, tempo de recarga

### 6.2 Veículos a Combustão
- **Autonomia:** 500-700 km
- **Capacidade:** 1-4 passageiros
- **Custo/km:** €0.20-€0.30
- **Tempo de reabastecimento:** 5-10 minutos
- **Emissões:** 120-180 g CO₂/km
- **Vantagens:** maior autonomia, reabastecimento rápido
- **Desvantagens:** maior custo, maior impacto ambiental

---

## 7. FUNCIONALIDADES EXTRA (ENCORAJADAS)

### 7.1 Predição e Otimização
- [ ] **Heurísticas de predição de procura** (padrões históricos)
- [ ] **Posicionamento proativo** em zonas de alta procura
- [ ] **Otimização de turnos** e distribuição ao longo do dia

### 7.2 Ride-Sharing
- [ ] **Algoritmos de partilha** (múltiplos passageiros)
- [ ] Compatibilidade de rotas
- [ ] Maximização de ocupação

### 7.3 Análise Estratégica
- [ ] **Análise custo-benefício** da expansão da frota elétrica
- [ ] Simulação de diferentes composições de frota
- [ ] ROI de investimento em infraestrutura

### 7.4 Integração Externa
- [ ] **Dados meteorológicos** (impacto da chuva na procura)
- [ ] Eventos especiais (jogos, concertos)
- [ ] Dados de tráfego em tempo real

### 7.5 Sistema de Incentivos
- [ ] **Promoção de veículos elétricos**
- [ ] Descontos para clientes que escolhem elétricos
- [ ] Gamificação para motoristas

---

## 8. ESTRUTURA DO CÓDIGO

### 8.1 Módulos Principais
```
/src
  /models
    - Vehicle.py         # Classe veículo (elétrico/combustão)
    - Request.py         # Classe pedido de transporte
    - City.py            # Grafo da cidade
    - Station.py         # Estações de recarga/abastecimento
  
  /algorithms
    - uninformed.py      # BFS, DFS, UCS
    - informed.py        # A*, Greedy, etc.
    - heuristics.py      # Funções heurísticas
  
  /simulation
    - simulator.py       # Motor de simulação
    - events.py          # Gestão de eventos dinâmicos
    - metrics.py         # Cálculo de métricas
  
  /utils
    - graph.py           # Estruturas de grafo
    - priority_queue.py  # Filas de prioridade
    - logger.py          # Sistema de logs
  
  /visualization
    - plotter.py         # Gráficos de resultados
    - map_viz.py         # Visualização do mapa
  
  - main.py              # Ponto de entrada
  - config.py            # Configurações globais
```

### 8.2 Estrutura de Dados
- Grafo: adjacência ou matriz
- Fila de prioridade para pedidos
- Estrutura para estado do sistema
- Hash/dicionário para veículos e localizações

---

## 9. RELATÓRIO

### 9.1 Estrutura Obrigatória
1. **Capa**
2. **Página de Avaliação pelos Pares** (imediatamente após a capa)
   - Lista de elementos com DELTAs
   - Soma dos DELTAs = 0.00
3. **Descrição do Problema**
4. **Formulação do Problema**
   - Estado inicial
   - Teste objetivo
   - Operadores
   - Custo da solução
5. **Descrição de Tarefas Realizadas**
   - Implementação do grafo
   - Algoritmos desenvolvidos
   - Sistema de simulação
   - Funcionalidades extra
6. **Decisões Tomadas pelo Grupo**
   - Escolhas de design
   - Estruturas de dados
   - Parâmetros de simulação
   - Trade-offs
7. **Sumário e Discussão dos Resultados**
   - Análise de métricas
   - Comparação de algoritmos
   - Gráficos e tabelas
   - Conclusões
8. **Bibliografia**
9. **Anexos** (se necessário)

### 9.2 Formato
- Ficheiro compactado: `IA-GRUPO[G].zip`
- Inclui código + relatório (PDF)
- Submissão via Blackboard

---

## 10. ASPETOS CRÍTICOS A NÃO ESQUECER

### 10.1 Implementação
- [ ] Comparação obrigatória entre algoritmos
- [ ] Métricas quantitativas todas implementadas
- [ ] Simulação dinâmica funcional
- [ ] Condições dinâmicas implementadas (trânsito, estradas cortadas, combustível)
- [ ] Grafo bem estruturado e eficiente

### 10.2 Testes e Validação
- [ ] Cenários de teste variados
- [ ] Casos extremos (frota esgotada, sem estações)
- [ ] Validação de resultados
- [ ] Reprodutibilidade

### 10.3 Relatório
- [ ] Página de avaliação pelos pares
- [ ] Formulação completa do problema
- [ ] Justificação de todas as decisões
- [ ] Análise crítica dos resultados
- [ ] Gráficos e visualizações

### 10.4 Prazos
- [ ] Entrega: 21 dezembro 2025
- [ ] Limite sem penalização: 9 janeiro 2026
- [ ] Apresentação: 12-16 janeiro 2026

---

## 11. CONDIÇÕES DINÂMICAS DETALHADAS

### 11.1 Trânsito Variável
- **Intensidade:** leve, moderado, intenso, congestionamento
- **Fator de impacto:** 1.0x - 3.0x no tempo de deslocação
- **Variação temporal:**
  - Rush matinal: 7h-9h
  - Rush vespertino: 17h-19h
  - Períodos calmos: restante
- **Variação geográfica:** zonas centrais mais congestionadas

### 11.2 Combustível/Autonomia
- **Consumo durante deslocação**
  - Elétricos: 15-20 kWh/100km
  - Combustão: 6-8 L/100km
- **Variação por condições:**
  - Trânsito: +20-30% consumo
  - Velocidade alta: +15% consumo
  - Ar condicionado: +10% consumo
- **Alertas de autonomia baixa:** <20% capacidade
- **Necessidade de recarga/reabastecimento urgente**

### 11.3 Estradas Cortadas
- **Probabilidade de ocorrência:** 1-5% por período
- **Duração:** 15-120 minutos
- **Causas:**
  - Obras programadas
  - Acidentes
  - Eventos especiais
  - Condições meteorológicas
- **Impacto:** rota alternativa obrigatória
- **Recálculo dinâmico de rotas**

### 11.4 Falhas em Estações
- **Estações de recarga:**
  - Ocupação total (fila de espera)
  - Avaria técnica (temporária)
  - Manutenção programada
- **Impacto:** necessidade de estação alternativa
- **Tempo de recuperação:** variável

---

## 12. BIBLIOGRAFIA RECOMENDADA

### Obrigatória
- **Russell and Norvig (2009).** Artificial Intelligence - A Modern Approach, 3rd edition
  - Capítulos 3-4: Search algorithms
  - Capítulo 6: Constraint satisfaction
  
- **Costa E., Simões A. (2008).** Inteligência Artificial - Fundamentos e Aplicações, FCA

### Complementar
- Algoritmos de otimização multi-objetivo
- Sistemas multi-agente
- Simulação de eventos discretos
- Algoritmos de roteamento em grafos dinâmicos

---

## 13. CHECKLIST FINAL

### Código
- [ ] Formulação do problema implementada
- [ ] Grafo da cidade criado
- [ ] Algoritmos não informados (≥2)
- [ ] Algoritmos informados (≥2)
- [ ] Heurísticas desenvolvidas
- [ ] Simulação dinâmica funcional
- [ ] Trânsito variável implementado
- [ ] Estradas cortadas implementadas
- [ ] Gestão de combustível/autonomia
- [ ] Todas as 6 métricas calculadas
- [ ] Sistema de testes
- [ ] Código comentado e documentado

### Relatório
- [ ] Capa
- [ ] Avaliação pelos pares (logo após capa)
- [ ] Descrição do problema
- [ ] Formulação completa
- [ ] Tarefas realizadas descritas
- [ ] Decisões justificadas
- [ ] Resultados com gráficos
- [ ] Discussão crítica
- [ ] Bibliografia
- [ ] Formato PDF

### Entrega
- [ ] Ficheiro compactado: IA-GRUPO[G].zip
- [ ] Código incluído
- [ ] Relatório incluído
- [ ] README com instruções de execução
- [ ] Submissão no Blackboard
- [ ] Antes de 21 dezembro 2025

---

**Última atualização:** 5 de novembro de 2025  
**Status:** Em desenvolvimento 🚧

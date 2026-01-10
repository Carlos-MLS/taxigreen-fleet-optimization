"""
Sistema de coleta e cálculo de métricas de desempenho.
Implementa as 6 métricas obrigatórias do trabalho.
"""

from typing import List, Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json


@dataclass
class PedidoMetrica:
    """Métricas de um pedido individual."""
    pedido_id: str
    tempo_criacao: float
    tempo_alocacao: Optional[float] = None
    tempo_inicio_servico: Optional[float] = None
    tempo_conclusao: Optional[float] = None
    veiculo_id: Optional[str] = None
    distancia_vazia: float = 0.0
    distancia_total: float = 0.0
    custo: float = 0.0
    emissoes: float = 0.0
    atendido: bool = False
    rejeitado: bool = False
    motivo_rejeicao: Optional[str] = None


@dataclass
class VeiculoMetrica:
    """Métricas de um veículo individual."""
    veiculo_id: str
    tempo_ocupado: float = 0.0
    tempo_disponivel: float = 0.0
    tempo_em_recarga: float = 0.0
    km_com_passageiros: float = 0.0
    km_sem_passageiros: float = 0.0
    pedidos_atendidos: int = 0
    num_recargas: int = 0
    custo_operacional: float = 0.0
    emissoes_total: float = 0.0


class MetricsCollector:
    """
    Coletor de métricas de desempenho do sistema.
    
    Métricas obrigatórias (conforme enunciado):
    1. Tempo médio de resposta ao pedido
    2. Taxa de ocupação da frota
    3. Custos operacionais totais
    4. Emissões de CO2 estimadas
    5. Número de pedidos não atendidos/rejeitados
    6. Km percorridos sem passageiros
    """
    
    def __init__(self):
        """Inicializa coletor de métricas."""
        self.pedidos: Dict[str, PedidoMetrica] = {}
        self.veiculos: Dict[str, VeiculoMetrica] = {}
        
        self.tempo_total_simulacao: float = 0.0
        self.inicio_simulacao: Optional[datetime] = None
        self.fim_simulacao: Optional[datetime] = None
        
        # Contadores globais
        self.total_pedidos: int = 0
        self.pedidos_atendidos: int = 0
        self.pedidos_rejeitados: int = 0
        self.pedidos_pendentes: int = 0
    
    def iniciar_simulacao(self):
        """Marca início da simulação."""
        self.inicio_simulacao = datetime.now()
    
    def finalizar_simulacao(self, tempo_total: float):
        """Marca fim da simulação."""
        self.fim_simulacao = datetime.now()
        self.tempo_total_simulacao = tempo_total
    
    def registrar_pedido(self, pedido_id: str, tempo_criacao: float):
        """Registra novo pedido."""
        self.pedidos[pedido_id] = PedidoMetrica(
            pedido_id=pedido_id,
            tempo_criacao=tempo_criacao
        )
        self.total_pedidos += 1
        self.pedidos_pendentes += 1
    
    def registrar_alocacao(
        self,
        pedido_id: str,
        veiculo_id: str,
        tempo_alocacao: float
    ):
        """Registra alocação de veículo a pedido."""
        if pedido_id in self.pedidos:
            self.pedidos[pedido_id].tempo_alocacao = tempo_alocacao
            self.pedidos[pedido_id].veiculo_id = veiculo_id
    
    def registrar_conclusao_pedido(
        self,
        pedido_id: str,
        tempo_conclusao: float,
        distancia_vazia: float,
        distancia_total: float,
        custo: float,
        emissoes: float
    ):
        """Registra conclusão de pedido."""
        if pedido_id in self.pedidos:
            metrica = self.pedidos[pedido_id]
            metrica.tempo_conclusao = tempo_conclusao
            metrica.distancia_vazia = distancia_vazia
            metrica.distancia_total = distancia_total
            metrica.custo = custo
            metrica.emissoes = emissoes
            metrica.atendido = True
            
            self.pedidos_atendidos += 1
            self.pedidos_pendentes -= 1
            
            # Atualizar métricas do veículo
            if metrica.veiculo_id:
                self._atualizar_metrica_veiculo(
                    metrica.veiculo_id,
                    distancia_total - distancia_vazia,
                    distancia_vazia,
                    custo,
                    emissoes
                )
    
    def registrar_rejeicao(
        self,
        pedido_id: str,
        tempo_rejeicao: float,
        motivo: str
    ):
        """Registra rejeição de pedido."""
        if pedido_id in self.pedidos:
            self.pedidos[pedido_id].rejeitado = True
            self.pedidos[pedido_id].motivo_rejeicao = motivo
            
            self.pedidos_rejeitados += 1
            self.pedidos_pendentes -= 1
    
    def registrar_veiculo(self, veiculo_id: str):
        """Registra novo veículo."""
        if veiculo_id not in self.veiculos:
            self.veiculos[veiculo_id] = VeiculoMetrica(veiculo_id=veiculo_id)
    
    def registrar_tempo_veiculo(
        self,
        veiculo_id: str,
        tempo_ocupado: float = 0.0,
        tempo_disponivel: float = 0.0,
        tempo_recarga: float = 0.0
    ):
        """Registra tempo do veículo em diferentes estados."""
        if veiculo_id not in self.veiculos:
            self.registrar_veiculo(veiculo_id)
        
        self.veiculos[veiculo_id].tempo_ocupado += tempo_ocupado
        self.veiculos[veiculo_id].tempo_disponivel += tempo_disponivel
        self.veiculos[veiculo_id].tempo_em_recarga += tempo_recarga
    
    def registrar_recarga(self, veiculo_id: str):
        """Registra recarga de veículo."""
        if veiculo_id in self.veiculos:
            self.veiculos[veiculo_id].num_recargas += 1
    
    def _atualizar_metrica_veiculo(
        self,
        veiculo_id: str,
        km_com_pass: float,
        km_sem_pass: float,
        custo: float,
        emissoes: float
    ):
        """Atualiza métricas do veículo."""
        if veiculo_id not in self.veiculos:
            self.registrar_veiculo(veiculo_id)
        
        v = self.veiculos[veiculo_id]
        v.km_com_passageiros += km_com_pass
        v.km_sem_passageiros += km_sem_pass
        v.pedidos_atendidos += 1
        v.custo_operacional += custo
        v.emissoes_total += emissoes
    
    # Cálculo das 6 métricas obrigatórias
    
    def calcular_tempo_medio_resposta(self) -> float:
        """
        Métrica 1: Tempo médio de resposta ao pedido.
        
        Tempo entre criação do pedido e início do atendimento.
        """
        tempos_resposta = []
        
        for pedido in self.pedidos.values():
            if pedido.atendido and pedido.tempo_alocacao is not None:
                tempo_resposta = pedido.tempo_alocacao - pedido.tempo_criacao
                tempos_resposta.append(tempo_resposta)
        
        if not tempos_resposta:
            return 0.0
        
        return sum(tempos_resposta) / len(tempos_resposta)
    
    def calcular_taxa_ocupacao_frota(self) -> float:
        """
        Métrica 2: Taxa de ocupação da frota.
        
        Percentagem do tempo que os veículos estão ocupados.
        """
        if not self.veiculos or self.tempo_total_simulacao == 0:
            return 0.0
        
        tempo_ocupado_total = sum(v.tempo_ocupado for v in self.veiculos.values())
        tempo_total_frota = self.tempo_total_simulacao * len(self.veiculos)
        
        if tempo_total_frota == 0:
            return 0.0
        
        return (tempo_ocupado_total / tempo_total_frota) * 100.0
    
    def calcular_custos_operacionais_totais(self) -> float:
        """
        Métrica 3: Custos operacionais totais.
        
        Soma de todos os custos de operação da frota.
        """
        return sum(v.custo_operacional for v in self.veiculos.values())
    
    def calcular_emissoes_co2_totais(self) -> float:
        """
        Métrica 4: Emissões de CO2 estimadas.
        
        Total de emissões de todos os veículos (kg CO2).
        """
        return sum(v.emissoes_total for v in self.veiculos.values())
    
    def calcular_pedidos_nao_atendidos(self) -> Dict[str, int]:
        """
        Métrica 5: Número de pedidos não atendidos/rejeitados.
        
        Returns:
            Dicionário com contagens de pedidos por estado
        """
        return {
            'total': self.total_pedidos,
            'atendidos': self.pedidos_atendidos,
            'rejeitados': self.pedidos_rejeitados,
            'pendentes': self.pedidos_pendentes,
            'taxa_atendimento': (self.pedidos_atendidos / self.total_pedidos * 100.0) if self.total_pedidos > 0 else 0.0
        }
    
    def calcular_km_vazios_totais(self) -> float:
        """
        Métrica 6: Km percorridos sem passageiros.
        
        Total de km percorridos vazios por toda a frota.
        """
        return sum(v.km_sem_passageiros for v in self.veiculos.values())
    
    # Métricas adicionais úteis
    
    def calcular_km_totais(self) -> Dict[str, float]:
        """Calcula km totais (com e sem passageiros)."""
        km_com_pass = sum(v.km_com_passageiros for v in self.veiculos.values())
        km_sem_pass = sum(v.km_sem_passageiros for v in self.veiculos.values())
        
        return {
            'km_com_passageiros': km_com_pass,
            'km_sem_passageiros': km_sem_pass,
            'km_totais': km_com_pass + km_sem_pass,
            'percentagem_vazios': (km_sem_pass / (km_com_pass + km_sem_pass) * 100.0) if (km_com_pass + km_sem_pass) > 0 else 0.0
        }
    
    def calcular_eficiencia_por_veiculo(self) -> Dict[str, Dict]:
        """Calcula eficiência individual de cada veículo."""
        resultado = {}
        
        for vid, v in self.veiculos.items():
            km_totais = v.km_com_passageiros + v.km_sem_passageiros
            
            resultado[vid] = {
                'pedidos_atendidos': v.pedidos_atendidos,
                'km_totais': km_totais,
                'km_vazios': v.km_sem_passageiros,
                'taxa_ocupacao': (v.tempo_ocupado / self.tempo_total_simulacao * 100.0) if self.tempo_total_simulacao > 0 else 0.0,
                'custo_por_pedido': (v.custo_operacional / v.pedidos_atendidos) if v.pedidos_atendidos > 0 else 0.0,
                'emissoes': v.emissoes_total,
                'num_recargas': v.num_recargas
            }
        
        return resultado
    
    def gerar_relatorio_completo(self) -> Dict:
        """
        Gera relatório completo com todas as métricas.
        
        Returns:
            Dicionário com todas as métricas calculadas
        """
        relatorio = {
            'resumo': {
                'tempo_total_simulacao': self.tempo_total_simulacao,
                'inicio': str(self.inicio_simulacao) if self.inicio_simulacao else None,
                'fim': str(self.fim_simulacao) if self.fim_simulacao else None,
                'num_veiculos': len(self.veiculos),
                'total_pedidos': self.total_pedidos
            },
            
            'metricas_obrigatorias': {
                '1_tempo_medio_resposta': {
                    'valor': self.calcular_tempo_medio_resposta(),
                    'unidade': 'minutos',
                    'descricao': 'Tempo médio entre criação e atendimento do pedido'
                },
                '2_taxa_ocupacao_frota': {
                    'valor': self.calcular_taxa_ocupacao_frota(),
                    'unidade': '%',
                    'descricao': 'Percentagem do tempo que os veículos estão ocupados'
                },
                '3_custos_operacionais': {
                    'valor': self.calcular_custos_operacionais_totais(),
                    'unidade': '€',
                    'descricao': 'Custos operacionais totais da frota'
                },
                '4_emissoes_co2': {
                    'valor': self.calcular_emissoes_co2_totais(),
                    'unidade': 'kg CO2',
                    'descricao': 'Emissões totais de CO2'
                },
                '5_pedidos_nao_atendidos': {
                    'valor': self.calcular_pedidos_nao_atendidos(),
                    'descricao': 'Estatísticas de atendimento de pedidos'
                },
                '6_km_vazios': {
                    'valor': self.calcular_km_vazios_totais(),
                    'unidade': 'km',
                    'descricao': 'Quilómetros percorridos sem passageiros'
                }
            },
            
            'metricas_adicionais': {
                'km_totais': self.calcular_km_totais(),
                'eficiencia_por_veiculo': self.calcular_eficiencia_por_veiculo()
            }
        }
        
        return relatorio
    
    def exportar_para_json(self, filepath: str):
        """Exporta relatório para arquivo JSON."""
        relatorio = self.gerar_relatorio_completo()
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(relatorio, f, indent=2, ensure_ascii=False)
    
    def imprimir_resumo(self):
        """Imprime resumo das métricas no console."""
        relatorio = self.gerar_relatorio_completo()
        
        print("\n" + "=" * 70)
        print(" RELATORIO DE METRICAS - TAXIGREEN ".center(70, '='))
        print("=" * 70)
        
        print(f"\n    Tempo Total de Simulacao: {self.tempo_total_simulacao:.1f} minutos")
        print(f"    Veiculos na Frota: {len(self.veiculos)}")
        print(f"    Total de Pedidos: {self.total_pedidos}")
        
        print("\n" + "-" * 70)
        print(" METRICAS OBRIGATORIAS ".center(70))
        print("-" * 70)
        
        metricas = relatorio['metricas_obrigatorias']
        
        print(f"\n[1] Tempo Medio de Resposta: {metricas['1_tempo_medio_resposta']['valor']:.2f} {metricas['1_tempo_medio_resposta']['unidade']}")
        print(f"[2] Taxa de Ocupacao da Frota: {metricas['2_taxa_ocupacao_frota']['valor']:.2f} {metricas['2_taxa_ocupacao_frota']['unidade']}")
        print(f"[3] Custos Operacionais: {metricas['3_custos_operacionais']['valor']:.2f} {metricas['3_custos_operacionais']['unidade']}")
        print(f"[4] Emissoes CO2: {metricas['4_emissoes_co2']['valor']:.2f} {metricas['4_emissoes_co2']['unidade']}")
        
        pedidos = metricas['5_pedidos_nao_atendidos']['valor']
        print(f"\n[5] Status dos Pedidos:")
        print(f"    - Atendidos: {pedidos['atendidos']} ({pedidos['taxa_atendimento']:.1f}%)")
        print(f"    - Rejeitados: {pedidos['rejeitados']}")
        print(f"    - Pendentes: {pedidos['pendentes']}")
        
        print(f"\n[6] Km Vazios: {metricas['6_km_vazios']['valor']:.2f} km")
        
        km = relatorio['metricas_adicionais']['km_totais']
        print(f"\n    Km Totais: {km['km_totais']:.2f} km")
        print(f"    - Com passageiros: {km['km_com_passageiros']:.2f} km")
        print(f"    - Sem passageiros: {km['km_sem_passageiros']:.2f} km ({km['percentagem_vazios']:.1f}%)")
        
        print("\n" + "=" * 70 + "\n")

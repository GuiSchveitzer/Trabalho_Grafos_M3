"""
Algoritmo Genético para o Problema do Caixeiro Viajante (PCV)
Implementação usando Partially Mapped Crossover (PMX) e seleção elitista
"""

import random
import math
from grafo import Grafo
from typing import List, Tuple, Dict


class IndividuoPCV:
    """Representa um indivíduo (rota) no Algoritmo Genético"""
    
    def __init__(self, rota: List[int], grafo: Grafo, cidade_inicial: int):
        """
        Args:
            rota: Lista de IDs de vértices representando a rota (sem repetir cidade inicial)
            grafo: Grafo com as cidades
            cidade_inicial: ID da cidade de partida/chegada
        """
        # Validar que a rota não tem duplicatas
        if len(rota) != len(set(rota)):
            raise ValueError(f"Rota contém cidades duplicadas: {rota}")
        
        # Validar que cidade_inicial não está na rota
        if cidade_inicial in rota:
            raise ValueError(f"Cidade inicial {cidade_inicial} não deve estar na rota")
        
        self.rota = rota
        self.grafo = grafo
        self.cidade_inicial = cidade_inicial
        self.custo = None
        self.calcular_custo()
    
    def calcular_custo(self):
        """Calcula o custo total da rota"""
        if len(self.rota) == 0:
            self.custo = float('inf')
            return
        
        # Começar da cidade inicial
        custo_total = 0
        rota_completa = [self.cidade_inicial] + self.rota + [self.cidade_inicial]
        
        # Calcular custo de cada segmento
        for i in range(len(rota_completa) - 1):
            cidade_atual = rota_completa[i]
            proxima_cidade = rota_completa[i + 1]
            
            peso = self.grafo.obter_peso_aresta(cidade_atual, proxima_cidade)
            
            if peso is None:
                # Aresta inexistente - penalizar com custo muito alto
                custo_total += 999999  # Valor tendendo ao infinito
            else:
                custo_total += peso
        
        self.custo = custo_total
        return custo_total
    
    def obter_rota_completa(self) -> List[int]:
        """Retorna a rota completa incluindo cidade inicial"""
        return [self.cidade_inicial] + self.rota + [self.cidade_inicial]
    
    def __str__(self):
        nomes = [self.grafo.obter_nome_vertice(v) for v in self.obter_rota_completa()]
        return f"Rota: {' → '.join(nomes)} | Custo: {self.custo}"
    
    def __lt__(self, outro):
        """Para ordenação por custo"""
        return self.custo < outro.custo


class AlgoritmoGeneticoPCV:
    """Implementação do Algoritmo Genético para resolver o PCV"""
    
    def __init__(self, grafo: Grafo, cidade_inicial: int, 
                 tamanho_populacao: int = 100,
                 taxa_cruzamento: float = 0.7,
                 taxa_mutacao: float = 0.01,
                 ponto1_cruzamento: int = 2,
                 ponto2_cruzamento: int = 5,
                 intervalo_geracao: float = 0.5):
        """
        Args:
            grafo: Grafo com as cidades
            cidade_inicial: ID da cidade de partida
            tamanho_populacao: Tamanho da população (mínimo 100)
            taxa_cruzamento: Taxa de cruzamento (0.6 - 0.8)
            taxa_mutacao: Taxa de mutação (0.005 - 0.01)
            ponto1_cruzamento: Primeiro ponto de corte para PMX
            ponto2_cruzamento: Segundo ponto de corte para PMX
            intervalo_geracao: Porcentagem da população substituída por geração
        """
        self.grafo = grafo
        self.cidade_inicial = cidade_inicial
        self.tamanho_populacao = max(100, tamanho_populacao)
        self.taxa_cruzamento = taxa_cruzamento
        self.taxa_mutacao = taxa_mutacao
        self.ponto1_cruzamento = ponto1_cruzamento
        self.ponto2_cruzamento = ponto2_cruzamento
        self.intervalo_geracao = intervalo_geracao
        
        # Cidades que precisam ser visitadas (todas exceto a inicial)
        todas_cidades = self.grafo.obter_todos_vertices()
        self.cidades_visitaveis = [c for c in todas_cidades if c != cidade_inicial]
        self.num_cidades = len(self.cidades_visitaveis)
        
        # População
        self.populacao: List[IndividuoPCV] = []
        self.melhor_individuo: IndividuoPCV = None
        self.historico_melhor_custo = []
        self.historico_custo_medio = []
        self.geracao_atual = 0
        
    def inicializar_populacao(self):
        """Gera população inicial de forma aleatória"""
        self.populacao = []
        
        for _ in range(self.tamanho_populacao):
            # Criar uma permutação aleatória das cidades (exceto a inicial)
            rota = self.cidades_visitaveis.copy()
            random.shuffle(rota)
            
            individuo = IndividuoPCV(rota, self.grafo, self.cidade_inicial)
            self.populacao.append(individuo)
        
        # Ordenar população por custo
        self.populacao.sort()
        self.melhor_individuo = self.populacao[0]
        
        # Registrar estatísticas
        self.registrar_estatisticas()
    
    def registrar_estatisticas(self):
        """Registra estatísticas da geração atual"""
        custos = [ind.custo for ind in self.populacao]
        self.historico_melhor_custo.append(min(custos))
        self.historico_custo_medio.append(sum(custos) / len(custos))
    
    def selecao_torneio(self, tamanho_torneio: int = 3) -> IndividuoPCV:
        """Seleção por torneio"""
        competidores = random.sample(self.populacao, tamanho_torneio)
        return min(competidores, key=lambda ind: ind.custo)
    
    def cruzamento_pmx(self, pai1: IndividuoPCV, pai2: IndividuoPCV) -> Tuple[List[int], List[int]]:
        """
        Partially Mapped Crossover (PMX) em 2 pontos fixos
        
        Args:
            pai1, pai2: Indivíduos pais
            
        Returns:
            Tupla com duas rotas filhas
        """
        n = len(pai1.rota)
        
        # Garantir que os pontos de corte estão válidos
        pt1 = min(self.ponto1_cruzamento, n - 1)
        pt2 = min(self.ponto2_cruzamento, n - 1)
        
        if pt1 > pt2:
            pt1, pt2 = pt2, pt1
        
        # Criar filhos copiando os pais
        filho1 = pai1.rota.copy()
        filho2 = pai2.rota.copy()
        
        # Segmento a ser trocado
        segmento1 = filho1[pt1:pt2+1]
        segmento2 = filho2[pt1:pt2+1]
        
        # Trocar segmentos
        filho1[pt1:pt2+1] = segmento2
        filho2[pt1:pt2+1] = segmento1
        
        # Corrigir conflitos no filho1
        for i in range(n):
            if i < pt1 or i > pt2:  # Fora do segmento trocado
                valor = filho1[i]
                
                # Se o valor está no segmento trocado, precisa ser substituído
                while valor in segmento2:
                    # Encontrar onde esse valor estava no pai2
                    idx_no_pai2 = pai2.rota.index(valor)
                    # Pegar o valor correspondente no pai1
                    valor = pai1.rota[idx_no_pai2]
                
                filho1[i] = valor
        
        # Corrigir conflitos no filho2
        for i in range(n):
            if i < pt1 or i > pt2:  # Fora do segmento trocado
                valor = filho2[i]
                
                # Se o valor está no segmento trocado, precisa ser substituído
                while valor in segmento1:
                    # Encontrar onde esse valor estava no pai1
                    idx_no_pai1 = pai1.rota.index(valor)
                    # Pegar o valor correspondente no pai2
                    valor = pai2.rota[idx_no_pai1]
                
                filho2[i] = valor
        
        return filho1, filho2
    
    def mutacao_swap(self, rota: List[int]) -> List[int]:
        """Mutação por troca de duas cidades aleatórias"""
        nova_rota = rota.copy()
        
        if len(nova_rota) > 1:
            # Escolher duas posições aleatórias
            i, j = random.sample(range(len(nova_rota)), 2)
            # Trocar
            nova_rota[i], nova_rota[j] = nova_rota[j], nova_rota[i]
        
        return nova_rota
    
    def mutacao_inversao(self, rota: List[int]) -> List[int]:
        """Mutação por inversão de um segmento da rota"""
        nova_rota = rota.copy()
        
        if len(nova_rota) > 1:
            # Escolher dois pontos
            i, j = sorted(random.sample(range(len(nova_rota)), 2))
            # Inverter segmento
            nova_rota[i:j+1] = reversed(nova_rota[i:j+1])
        
        return nova_rota
    
    def evoluir_geracao(self):
        """Evolui uma geração completa"""
        self.geracao_atual += 1
        
        # Calcular quantos indivíduos serão substituídos
        num_substituicoes = int(self.tamanho_populacao * self.intervalo_geracao)
        num_elitismo = self.tamanho_populacao - num_substituicoes
        
        # Seleção elitista - manter os melhores
        nova_populacao = self.populacao[:num_elitismo]
        
        # Gerar novos indivíduos
        while len(nova_populacao) < self.tamanho_populacao:
            # Selecionar pais
            pai1 = self.selecao_torneio()
            pai2 = self.selecao_torneio()
            
            # Cruzamento
            if random.random() < self.taxa_cruzamento:
                rota_filho1, rota_filho2 = self.cruzamento_pmx(pai1, pai2)
            else:
                rota_filho1, rota_filho2 = pai1.rota.copy(), pai2.rota.copy()
            
            # Mutação
            if random.random() < self.taxa_mutacao:
                # Alternar entre swap e inversão
                if random.random() < 0.5:
                    rota_filho1 = self.mutacao_swap(rota_filho1)
                else:
                    rota_filho1 = self.mutacao_inversao(rota_filho1)
            
            if random.random() < self.taxa_mutacao:
                if random.random() < 0.5:
                    rota_filho2 = self.mutacao_swap(rota_filho2)
                else:
                    rota_filho2 = self.mutacao_inversao(rota_filho2)
            
            # Criar indivíduos
            filho1 = IndividuoPCV(rota_filho1, self.grafo, self.cidade_inicial)
            filho2 = IndividuoPCV(rota_filho2, self.grafo, self.cidade_inicial)
            
            nova_populacao.append(filho1)
            if len(nova_populacao) < self.tamanho_populacao:
                nova_populacao.append(filho2)
        
        # Atualizar população
        self.populacao = nova_populacao
        
        # Ordenar por custo
        self.populacao.sort()
        
        # Atualizar melhor indivíduo
        if self.populacao[0].custo < self.melhor_individuo.custo:
            self.melhor_individuo = self.populacao[0]
        
        # Registrar estatísticas
        self.registrar_estatisticas()
    
    def executar(self, max_geracoes: int = 20, callback_geracao=None) -> IndividuoPCV:
        """
        Executa o algoritmo genético
        
        Args:
            max_geracoes: Número máximo de gerações
            callback_geracao: Função chamada após cada geração callback(geracao, ag)
            
        Returns:
            Melhor indivíduo encontrado
        """
        # Inicializar população
        self.inicializar_populacao()
        
        if callback_geracao:
            callback_geracao(0, self)
        
        # Evoluir gerações
        for geracao in range(max_geracoes):
            self.evoluir_geracao()
            
            if callback_geracao:
                callback_geracao(self.geracao_atual, self)
        
        return self.melhor_individuo
    
    def obter_estatisticas_geracao(self) -> Dict:
        """Retorna estatísticas da geração atual"""
        custos = [ind.custo for ind in self.populacao]
        rotas_validas = [ind for ind in self.populacao if ind.custo < 999999]
        
        return {
            'geracao': self.geracao_atual,
            'melhor_custo': min(custos),
            'custo_medio': sum(custos) / len(custos),
            'pior_custo': max(custos),
            'num_rotas_validas': len(rotas_validas),
            'melhor_individuo': self.melhor_individuo,
            'top_10': self.populacao[:10]
        }
    
    def obter_melhores_individuos(self, n: int = 10) -> List[IndividuoPCV]:
        """Retorna os n melhores indivíduos da população"""
        return self.populacao[:n]
    
    def calcular_diversidade(self) -> float:
        """Calcula a diversidade genética da população"""
        if len(self.populacao) < 2:
            return 0.0
        
        # Calcular diversidade como desvio padrão dos custos
        custos = [ind.custo for ind in self.populacao]
        media = sum(custos) / len(custos)
        variancia = sum((c - media) ** 2 for c in custos) / len(custos)
        return math.sqrt(variancia)

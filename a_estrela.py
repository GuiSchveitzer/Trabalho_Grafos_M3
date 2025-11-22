import heapq
from grafo import Grafo
from dados import calcular_distancia_manhattan, HEURISTICA_PARA_CASCAVEL

class AEstrela:
    """Implementação do algoritmo A* para busca de caminho mínimo"""
    
    def __init__(self, grafo):
        self.grafo = grafo
        self.caminho = []
        self.custo_total = 0
        
    def encontrar_caminho(self, inicio, destino):
        """
        Encontra o caminho mínimo entre inicio e destino usando A*
        """
        # Inicialização
        conjunto_aberto = []  # Fila de prioridade: (f_score, vertice)
        heapq.heappush(conjunto_aberto, (0, inicio))
        
        veio_de = {}  # Para reconstruir o caminho
        g_score = {vertice: float('inf') for vertice in self.grafo.obter_todos_vertices()}
        g_score[inicio] = 0
        
        f_score = {vertice: float('inf') for vertice in self.grafo.obter_todos_vertices()}
        f_score[inicio] = self.heuristica(inicio, destino)
        
        conjunto_fechado = set()  # Nós já completamente explorados
        
        while conjunto_aberto:
            f_atual, atual = heapq.heappop(conjunto_aberto)
            
            # Se já foi completamente explorado, pular
            if atual in conjunto_fechado:
                continue
            
            # Marca como explorado
            conjunto_fechado.add(atual)
            
            # Se chegou ao destino
            if atual == destino:
                self.caminho = self.reconstruir_caminho(veio_de, atual)
                self.custo_total = g_score[atual]
                return self.caminho, self.custo_total
            
            # Explora vizinhos
            for vizinho, peso in self.grafo.obter_vizinhos(atual):
                # Se já foi completamente explorado, não precisa processar
                if vizinho in conjunto_fechado:
                    continue
                
                g_score_tentativo = g_score[atual] + peso
                
                if g_score_tentativo < g_score[vizinho]:
                    # Este caminho é melhor
                    veio_de[vizinho] = atual
                    g_score[vizinho] = g_score_tentativo
                    f_score[vizinho] = g_score[vizinho] + self.heuristica(vizinho, destino)

                    # Adiciona à fila (será visitado depois se for promissor)
                    heapq.heappush(conjunto_aberto, (f_score[vizinho], vizinho))
            
            # DEBUG: Mostra estado atual da fila de prioridade
            if conjunto_aberto:
                print(f"\n  📋 Fila de prioridade após explorar {self.grafo.obter_nome_vertice(atual)}:")
                # Criar uma cópia ordenada para visualização (sem alterar a heap original)
                fila_ordenada = sorted(conjunto_aberto)
                for f_val, v_id in fila_ordenada[:5]:  # Mostra os 5 primeiros
                    nome = self.grafo.obter_nome_vertice(v_id)
                    if v_id not in conjunto_fechado:  # Só mostra se ainda não foi explorado
                        print(f"     • {nome:20} (f={f_val:6.1f})")
                if len([v for _, v in fila_ordenada if v not in conjunto_fechado]) > 5:
                    print(f"     ... e mais {len([v for _, v in fila_ordenada if v not in conjunto_fechado]) - 5} nós na fila")
            else:
                print(f"  📋 Fila vazia após explorar {self.grafo.obter_nome_vertice(atual)}")
            print()
        
    def heuristica(self, vertice1, vertice2):
        """
        Calcula a heurística h(n) usando distância de Manhattan
        entre as coordenadas geográficas dos vértices.
        """
        nome_destino = self.grafo.obter_nome_vertice(vertice2)
        nome_origem = self.grafo.obter_nome_vertice(vertice1)
        
        # Se o destino for Cascavel, usar tabela pré-calculada
        if nome_destino == 'Cascavel' and nome_origem in HEURISTICA_PARA_CASCAVEL:
            return HEURISTICA_PARA_CASCAVEL[nome_origem]
        
        # Caso contrário, calcular dinamicamente
        pos1 = self.grafo.obter_posicao_vertice(vertice1)
        pos2 = self.grafo.obter_posicao_vertice(vertice2)
        
        if pos1 is None or pos2 is None:
            return 0
        
        return calcular_distancia_manhattan(pos1, pos2)
    
    def reconstruir_caminho(self, veio_de, atual):
        """Reconstrói o caminho do início ao fim"""
        caminho = [atual]
        while atual in veio_de:
            atual = veio_de[atual]
            caminho.append(atual)
        caminho.reverse()
        return caminho
    
    def obter_arestas_caminho(self):
        """
        Retorna as arestas do caminho encontrado
        Útil para visualização
        """
        if not self.caminho or len(self.caminho) < 2:
            return []
        
        arestas = []
        for i in range(len(self.caminho) - 1):
            arestas.append((self.caminho[i], self.caminho[i+1]))
        
        return arestas
    
    def obter_detalhes_caminho(self):
        """
        Retorna detalhes do caminho encontrado
        """
        if not self.caminho:
            return None
        
        detalhes = {
            'caminho': [self.grafo.obter_nome_vertice(v) for v in self.caminho],
            'ids_caminho': self.caminho,
            'custo_total': self.custo_total,
            'num_vertices': len(self.caminho),
            'arestas': []
        }
        
        # Adiciona detalhes de cada segmento
        for i in range(len(self.caminho) - 1):
            v1, v2 = self.caminho[i], self.caminho[i+1]
            peso = self.grafo.obter_peso_aresta(v1, v2)
            detalhes['arestas'].append({
                'de': self.grafo.obter_nome_vertice(v1),
                'para': self.grafo.obter_nome_vertice(v2),
                'distancia': peso
            })
        
        return detalhes
    
    def calcular_tabela_heuristica(self, destino):
        """
        Calcula a tabela h(n) para todos os vértices em relação ao destino.
        Se o destino for Cascavel, usa a tabela pré-calculada.
        Caso contrário, calcula usando distância de Manhattan.
        """
        nome_destino = self.grafo.obter_nome_vertice(destino)
        tabela_heuristica = {}
        
        # Se o destino for Cascavel, usar tabela pré-calculada
        if nome_destino == 'Cascavel':
            for vertice in self.grafo.obter_todos_vertices():
                nome_vertice = self.grafo.obter_nome_vertice(vertice)
                if nome_vertice in HEURISTICA_PARA_CASCAVEL:
                    tabela_heuristica[nome_vertice] = HEURISTICA_PARA_CASCAVEL[nome_vertice]
                else:
                    # Fallback caso não esteja na tabela
                    valor_h = self.heuristica(vertice, destino)
                    tabela_heuristica[nome_vertice] = valor_h
        else:
            # Calcular dinamicamente para outros destinos
            for vertice in self.grafo.obter_todos_vertices():
                valor_h = self.heuristica(vertice, destino)
                tabela_heuristica[self.grafo.obter_nome_vertice(vertice)] = valor_h
        
        return tabela_heuristica

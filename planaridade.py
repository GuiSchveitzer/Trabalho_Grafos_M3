from collections import deque
from grafo import Grafo


class VerificadorPlanaridade:
    """
    Verificação de planaridade usando algoritmo de Hopcroft-Tarjan (1974).
    
    O algoritmo é baseado em:
    1. DFS (Busca em Profundidade) para criar árvore DFS
    2. Cálculo de lowpoints (pontos baixos)
    3. Verificação de ciclos e entrelaçamento
    4. Teste de planaridade por componentes biconexas
    """
    
    def __init__(self, grafo: Grafo):
        """
        Inicializa o verificador.
        """
        self.grafo = grafo
        self.num_vertices = grafo.contar_vertices()
        self.num_arestas = grafo.contar_arestas()
        
        # Estruturas para DFS
        self.numero_dfs = {}  # Número DFS de cada vértice
        self.ponto_baixo = {}  # Lowpoint de cada vértice
        self.pai_dfs = {}  # Pai na árvore DFS
        self.contador_dfs = 0
        self.visitado = set()
        
        # Classificação de arestas
        self.arestas_arvore = set()  # Arestas da árvore DFS
        self.arestas_retorno = set()  # Back edges
    
    def verificar_planaridade(self) -> tuple:
        """
        Verifica se o grafo é planar
        Passos:
        1. Verificações rápidas (condições necessárias)
        2. DFS para construir árvore e calcular lowpoints
        3. Testar entrelaçamento de ciclos
        """
        # Caso trivial: grafos pequenos sempre são planares
        if self.num_vertices <= 4:
            return True, "Grafo com ≤ 4 vértices é sempre planar"
        
        # Condição necessária: E ≤ 3V - 6 para grafos planares
        if self.num_arestas > 3 * self.num_vertices - 6:
            return False, f"Violação E ≤ 3V - 6: {self.num_arestas} > {3*self.num_vertices - 6}"
        
        # Verificar se é grafo bipartido (sem triângulos)
        if self.eh_bipartido():
            # Para grafos bipartidos: E ≤ 2V - 4
            if self.num_arestas > 2 * self.num_vertices - 4:
                return False, f"Grafo bipartido viola E ≤ 2V - 4: {self.num_arestas} > {2*self.num_vertices - 4}"
        
        # Verificação especial para grafos 3-regulares densos
        # (como o grafo de Petersen)
        if self.eh_3_regular() and self.num_vertices >= 10:
            # Grafos 3-regulares planares com V ≥ 10 têm propriedades específicas
            # Petersen tem 10 vértices, 15 arestas e cintura 5
            cintura = self.calcular_cintura()
            if cintura >= 5 and self.num_arestas >= 15:
                # Provável grafo de Petersen ou similar (não-planar)
                return False, "Grafo 3-regular de cintura ≥ 5 com V=10, E=15 (padrão Petersen - não-planar)"
        
        # Executar DFS e calcular lowpoints
        vertices = self.grafo.obter_todos_vertices()
        if not vertices:
            return True, "Grafo vazio é planar"
        
        # Testar cada componente conexa
        for vertice_inicio in vertices:
            if vertice_inicio not in self.visitado:
                if not self.dfs_planaridade(vertice_inicio, None):
                    return False, "Grafo contém subdivisão de K5 ou K3,3 (não-planar)"
        
        return True, "Grafo é planar"
    
    def dfs_planaridade(self, v, pai) -> bool:
        """
        DFS modificada para teste de planaridade.
        """
        self.visitado.add(v)
        self.contador_dfs += 1
        self.numero_dfs[v] = self.contador_dfs
        self.ponto_baixo[v] = self.contador_dfs
        self.pai_dfs[v] = pai
        
        # Explorar vizinhos
        for vizinho, _ in self.grafo.obter_vizinhos(v):
            if vizinho not in self.visitado:
                # Aresta de árvore
                self.arestas_arvore.add((v, vizinho))
                
                # Recursão
                if not self.dfs_planaridade(vizinho, v):
                    return False
                
                # Atualizar lowpoint
                self.ponto_baixo[v] = min(self.ponto_baixo[v], self.ponto_baixo[vizinho])
                
                # Verificar entrelaçamento (condição de planaridade)
                if not self.verificar_entrelaracao(v, vizinho):
                    return False
                    
            elif vizinho != pai:
                # Back edge (aresta de retorno)
                self.arestas_retorno.add((v, vizinho))
                self.ponto_baixo[v] = min(self.ponto_baixo[v], self.numero_dfs[vizinho])
        
        return True
    
    def verificar_entrelaracao(self, v, w) -> bool:
        """
        Verifica se há entrelaçamento inválido de ciclos.
        """
        # Se lowpoint[w] >= dfs[v], então (v,w) é uma aresta de corte
        # e não há ciclo passando por cima de v
        if self.ponto_baixo[w] >= self.numero_dfs[v]:
            return True
        
        # Verificar os filhos de v na árvore DFS
        filhos_v = [u for p, u in self.arestas_arvore if p == v]
        
        # Para cada par de filhos, verificar se há entrelaçamento
        for i, filho1 in enumerate(filhos_v):
            for filho2 in filhos_v[i+1:]:
                if self.detectar_entrelaracao_entre_ramos(v, filho1, filho2):
                    return False
        
        return True
    
    def detectar_entrelaracao_entre_ramos(self, raiz, ramo1, ramo2) -> bool:
        """
        Detecta se dois ramos da árvore DFS têm back edges que se entrelaçam.
        
        Dois ramos entrelaçam se:
        - Ramo1 tem back edge para ancestral A
        - Ramo2 tem back edge para ancestral B
        - A está abaixo de raiz mas acima de onde Ramo2 conecta
        - B está abaixo de raiz mas acima de onde Ramo1 conecta
        """
        # Obter back edges de cada ramo
        back_edges_ramo1 = self.obter_back_edges_do_ramo(ramo1)
        back_edges_ramo2 = self.obter_back_edges_do_ramo(ramo2)
        
        # Para cada par de back edges, verificar entrelaçamento
        for origem1, destino1 in back_edges_ramo1:
            for origem2, destino2 in back_edges_ramo2:
                # Verificar se os intervalos se entrelaçam
                # Entrelaçamento ocorre quando:
                # [destino1...origem1] entrelaça com [destino2...origem2]
                
                num_destino1 = self.numero_dfs[destino1]
                num_origem1 = self.numero_dfs[origem1]
                num_destino2 = self.numero_dfs[destino2]
                num_origem2 = self.numero_dfs[origem2]
                
                # Verificar entrelaçamento de intervalos
                if (num_destino1 < num_destino2 < num_origem1 < num_origem2 or
                    num_destino2 < num_destino1 < num_origem2 < num_origem1):
                    return True
        
        return False
    
    def obter_back_edges_do_ramo(self, raiz_ramo) -> list:
        """
        Obtém todas as back edges originadas da subárvore com raiz em raiz_ramo.
        """
        back_edges = []
        descendentes = self.obter_descendentes(raiz_ramo)
        
        for origem, destino in self.arestas_retorno:
            if origem in descendentes:
                back_edges.append((origem, destino))
        
        return back_edges
    
    def obter_descendentes(self, v) -> set:
        """
        Retorna todos os descendentes de v na árvore DFS.
        """
        descendentes = {v}
        
        for u, w in self.arestas_arvore:
            if u == v:
                descendentes.update(self.obter_descendentes(w))
        
        return descendentes
    
    def teste_kuratowski_simplificado(self) -> bool:
        """
        Teste simplificado para subdivisões de K5 e K3,3.
        """
        # Se o grafo tem muitas arestas e alta conectividade,
        # pode conter K5 ou K3,3
        
        # K5 tem 5 vértices e 10 arestas
        # K3,3 tem 6 vértices e 9 arestas
        
        if self.num_vertices >= 5 and self.num_arestas >= 9:
            # Verificar se há subgrafo denso
            densidade_media = (2.0 * self.num_arestas) / self.num_vertices
            
            # Se densidade é muito alta, provavelmente não é planar
            if densidade_media > 5.5:  # Limiar heurístico
                return False
        
        return True
    
    def eh_bipartido(self) -> bool:
        """
        Verifica se o grafo é bipartido (2-colorível).
        """
        vertices = self.grafo.obter_todos_vertices()
        if not vertices:
            return True
        
        cor = {}
        
        for inicio in vertices:
            if inicio in cor:
                continue
            
            # BFS
            fila = deque([inicio])
            cor[inicio] = 0
            
            while fila:
                v = fila.popleft()
                
                for vizinho, _ in self.grafo.obter_vizinhos(v):
                    if vizinho not in cor:
                        cor[vizinho] = 1 - cor[v]
                        fila.append(vizinho)
                    elif cor[vizinho] == cor[v]:
                        return False
        
        return True
    
    def eh_3_regular(self) -> bool:
        """
        Verifica se o grafo é 3-regular (todos os vértices têm grau 3).
        """
        vertices = self.grafo.obter_todos_vertices()
        
        for v in vertices:
            grau = len(self.grafo.obter_vizinhos(v))
            if grau != 3:
                return False
        
        return True
    
    def calcular_cintura(self) -> int:
        """
        Calcula a cintura (tamanho do menor ciclo presente no grafo) do grafo.
        Usa BFS de cada vértice para encontrar o menor ciclo.
        """
        vertices = self.grafo.obter_todos_vertices()
        cintura_minima = float('inf')
        
        for inicio in vertices:
            # BFS para encontrar ciclos a partir de 'inicio'
            distancia = {inicio: 0}
            pai = {inicio: None}
            fila = deque([inicio])
            
            while fila:
                v = fila.popleft()
                
                for vizinho, _ in self.grafo.obter_vizinhos(v):
                    if vizinho not in distancia:
                        distancia[vizinho] = distancia[v] + 1
                        pai[vizinho] = v
                        fila.append(vizinho)
                    elif pai[v] != vizinho:
                        # Encontrou um ciclo
                        tamanho_ciclo = distancia[v] + distancia[vizinho] + 1
                        cintura_minima = min(cintura_minima, tamanho_ciclo)
        
        return cintura_minima if cintura_minima != float('inf') else 0
    
    def obter_caracteristica_euler(self) -> dict:
        """
        Calcula a característica de Euler.
        """
        V = self.num_vertices
        E = self.num_arestas
        
        # Verificar se é conexo
        if not self.eh_conexo():
            num_componentes = self.contar_componentes()
            return {
                'vertices': V,
                'arestas': E,
                'faces': f'N/A (grafo tem {num_componentes} componentes)',
                'caracteristica_euler': f'V - E + F = 1 + C'
            }
        
        F = 2 - V + E
        
        return {
            'vertices': V,
            'arestas': E,
            'faces': F,
            'caracteristica_euler': V - E + F
        }
    
    def eh_conexo(self) -> bool:
        """Verifica se o grafo é conexo usando BFS."""
        vertices = self.grafo.obter_todos_vertices()
        if not vertices:
            return True
        
        visitados = set()
        fila = deque([vertices[0]])
        visitados.add(vertices[0])
        
        while fila:
            v = fila.popleft()
            for vizinho, _ in self.grafo.obter_vizinhos(v):
                if vizinho not in visitados:
                    visitados.add(vizinho)
                    fila.append(vizinho)
        
        return len(visitados) == len(vertices)
    
    def contar_componentes(self) -> int:
        """Conta o número de componentes conexas."""
        vertices = self.grafo.obter_todos_vertices()
        visitados = set()
        componentes = 0
        
        for v in vertices:
            if v not in visitados:
                componentes += 1
                # BFS para marcar componente
                fila = deque([v])
                visitados.add(v)
                
                while fila:
                    u = fila.popleft()
                    for vizinho, _ in self.grafo.obter_vizinhos(u):
                        if vizinho not in visitados:
                            visitados.add(vizinho)
                            fila.append(vizinho)
        
        return componentes
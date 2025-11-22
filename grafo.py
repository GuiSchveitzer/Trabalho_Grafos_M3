class Grafo:
    """Classe para representação de um grafo não direcionado"""
    
    def __init__(self):
        self.vertices = {}  # {vertice: {'x': x, 'y': y, 'nome': nome}}
        self.arestas = []  # [(v1, v2, peso)]
        self.lista_adjacencia = {}  # {vertice: [(vizinho, peso)]}
        
    def adicionar_vertice(self, id_vertice, nome=None, x=None, y=None):
        """Adiciona um vértice ao grafo"""
        self.vertices[id_vertice] = {
            'nome': nome if nome else str(id_vertice),
            'x': x,
            'y': y
        }
        if id_vertice not in self.lista_adjacencia:
            self.lista_adjacencia[id_vertice] = []
            
    def adicionar_aresta(self, v1, v2, peso=1):
        """Adiciona uma aresta entre dois vértices"""
        if v1 not in self.vertices or v2 not in self.vertices:
            raise ValueError("Vértices devem existir antes de adicionar aresta")
        
        # Evita arestas duplicadas
        if not any((v1 == a[0] and v2 == a[1]) or (v1 == a[1] and v2 == a[0]) for a in self.arestas):
            self.arestas.append((v1, v2, peso))
            self.lista_adjacencia[v1].append((v2, peso))
            self.lista_adjacencia[v2].append((v1, peso))
            
    def obter_posicao_vertice(self, id_vertice):
        """Retorna as coordenadas (x, y) de um vértice"""
        v = self.vertices.get(id_vertice)
        if v:
            return (v['x'], v['y'])
        return None
    
    def obter_nome_vertice(self, id_vertice):
        """Retorna o nome de um vértice"""
        v = self.vertices.get(id_vertice)
        if v:
            return v['nome']
        return str(id_vertice)
    
    def obter_vizinhos(self, id_vertice):
        """Retorna os vizinhos de um vértice"""
        return self.lista_adjacencia.get(id_vertice, [])
    
    def obter_peso_aresta(self, v1, v2):
        """Retorna o peso da aresta entre dois vértices"""
        for aresta in self.arestas:
            if (aresta[0] == v1 and aresta[1] == v2) or (aresta[0] == v2 and aresta[1] == v1):
                return aresta[2]
        return None
    
    def obter_grau(self, id_vertice):
        """Retorna o grau de um vértice"""
        return len(self.lista_adjacencia.get(id_vertice, []))
    
    def obter_todos_vertices(self):
        """Retorna lista de todos os vértices"""
        return list(self.vertices.keys())
    
    def obter_todas_arestas(self):
        """Retorna lista de todas as arestas"""
        return self.arestas
    
    def contar_vertices(self):
        """Retorna o número de vértices"""
        return len(self.vertices)
    
    def contar_arestas(self):
        """Retorna o número de arestas"""
        return len(self.arestas)
    
    def __str__(self):
        resultado = f"Grafo com {self.contar_vertices()} vértices e {self.contar_arestas()} arestas\n"
        resultado += "Vértices: " + ", ".join([self.obter_nome_vertice(v) for v in self.vertices]) + "\n"
        resultado += "Arestas:\n"
        for v1, v2, p in self.arestas:
            resultado += f"  {self.obter_nome_vertice(v1)} -- {self.obter_nome_vertice(v2)} (peso: {p})\n"
        return resultado

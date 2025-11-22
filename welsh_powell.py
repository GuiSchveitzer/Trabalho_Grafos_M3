from grafo import Grafo

class WelshPowell:
    """Implementação do algoritmo Welsh-Powell para coloração de grafos"""
    
    def __init__(self, grafo):
        self.grafo = grafo
        self.cores = {}  # {vertice: cor}
        self.passos = []  # Lista de passos para visualização
        
    def color_graph(self, registrar_passos=False):
        """
        Aplica o algoritmo Welsh-Powell para colorir o grafo
        
        1. Ordenar vértices em ordem decrescente de grau
        2. Usar cor 1 para o primeiro vértice e todos os não-adjacentes a ele
        3. Usar cor 2 para o próximo sem cor e todos os não-adjacentes com cor 2
        4. Continuar até todos terem cor
        """
        vertices = self.grafo.obter_todos_vertices()
        
        # Passo 1: Ordenar vértices por grau (decrescente)
        vertices_ordenados = sorted(
            vertices, 
            key=lambda v: self.grafo.obter_grau(v), 
            reverse=True
        )
        
        if registrar_passos:
            self.passos = []
            graus = {v: self.grafo.obter_grau(v) for v in vertices_ordenados}
            self.passos.append({
                'tipo': 'ordenacao',
                'descricao': 'Passo 1: Ordenar vértices por grau (decrescente)',
                'vertices_ordenados': vertices_ordenados,
                'graus': graus,
                'cores_atuais': {}
            })
        
        self.cores = {}
        cor_atual = 0
        passo_contador = 2
        
        # Continuar até todos os vértices terem cor
        while len(self.cores) < len(vertices_ordenados):
            # Encontrar primeiro vértice sem cor
            vertice_base = None
            for v in vertices_ordenados:
                if v not in self.cores:
                    vertice_base = v
                    break
            
            if vertice_base is None:
                break
            
            # Colorir vértice base
            self.cores[vertice_base] = cor_atual
            vertices_coloridos_neste_passo = [vertice_base]
            
            # Obter vizinhos do vértice base
            vizinhos_base = set()
            for viz, _ in self.grafo.obter_vizinhos(vertice_base):
                vizinhos_base.add(viz)
            
            # Tentar colorir outros vértices com a mesma cor
            # (aqueles que não são adjacentes ao vértice base nem aos já coloridos neste passo)
            for v in vertices_ordenados:
                if v in self.cores:
                    continue
                
                # Verificar se v é adjacente a algum vértice já colorido com cor_atual
                pode_colorir = True
                
                # Obter todos os vizinhos de v
                vizinhos_v = set()
                for viz, _ in self.grafo.obter_vizinhos(v):
                    vizinhos_v.add(viz)
                
                # Verificar se v é adjacente a algum vértice com cor_atual
                for vertice_colorido in vertices_coloridos_neste_passo:
                    if vertice_colorido in vizinhos_v:
                        pode_colorir = False
                        break
                
                if pode_colorir:
                    self.cores[v] = cor_atual
                    vertices_coloridos_neste_passo.append(v)
            
            if registrar_passos:
                nomes_coloridos = [self.grafo.obter_nome_vertice(v) for v in vertices_coloridos_neste_passo]
                self.passos.append({
                    'tipo': 'coloracao_grupo',
                    'descricao': f'Passo {passo_contador}: Associar cor {cor_atual} aos vértices não-adjacentes',
                    'cor_atual': cor_atual,
                    'vertices_coloridos': vertices_coloridos_neste_passo,
                    'nomes_vertices': nomes_coloridos,
                    'cores_atuais': self.cores.copy()
                })
                passo_contador += 1
            
            # Próxima cor
            cor_atual += 1
        
        return self.cores
    
    def obter_passos(self):
        """
        Retorna a lista de passos registrados durante a execução
        """
        return self.passos
    
    def get_chromatic_number(self):
        """
        Retorna o número cromático (número de cores usadas)
        """
        if not self.cores:
            self.color_graph()
        
        return max(self.cores.values()) + 1 if self.cores else 0
    
    def get_color_classes(self):
        """
        Retorna as classes de cores (conjuntos independentes)
        """
        if not self.cores:
            self.color_graph()
        
        classes_cores = {}
        for vertice, cor in self.cores.items():
            if cor not in classes_cores:
                classes_cores[cor] = []
            classes_cores[cor].append(vertice)
        
        return classes_cores
    
    def verify_coloring(self):
        """
        Verifica se a coloração é válida (vértices adjacentes têm cores diferentes)
        """
        if not self.cores:
            return False, "Grafo não foi colorido"
        
        for v1, v2, _ in self.grafo.obter_todas_arestas():
            if self.cores[v1] == self.cores[v2]:
                return False, f"Vértices adjacentes {self.grafo.obter_nome_vertice(v1)} e {self.grafo.obter_nome_vertice(v2)} têm a mesma cor"
        
        return True, "Coloração válida"
    
    def get_statistics(self):
        """
        Retorna estatísticas sobre a coloração
        """
        if not self.cores:
            self.color_graph()
        
        classes_cores = self.get_color_classes()
        numero_cromatico = self.get_chromatic_number()
        eh_valida, mensagem = self.verify_coloring()
        
        return {
            'chromatic_number': numero_cromatico,
            'colors_used': list(range(numero_cromatico)),
            'color_distribution': {f"Cor {c}": len(vertices) for c, vertices in classes_cores.items()},
            'is_valid': eh_valida,
            'validation_message': mensagem
        }


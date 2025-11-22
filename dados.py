# ============================================================================
# GRAFO DO TRABALHO 3 - Algoritmo Genético para PCV
# ============================================================================
# Coordenadas das cidades do grafo fornecido (posições aproximadas para visualização)
COORDENADAS_CIDADES = {
    'F': (0, 2),      # Canto inferior esquerdo
    'N': (2, 4),      # Superior esquerdo
    'C': (2.5, 2.5),  # Centro-esquerdo
    'L': (2, 0),      # Inferior centro-esquerdo
    'K': (4, 4),      # Superior centro
    'E': (5, 2.5),    # Centro-direita
    'H': (4, 0),      # Inferior centro-direita
    'G': (7, 3),      # Superior direito
}

# Arestas do grafo (cidade1, cidade2, peso/distância)
# Baseado no grafo fornecido na imagem
ARESTAS = [
    # Arestas conectadas a F
    ('F', 'N', 30),
    ('F', 'C', 20),
    ('F', 'L', 10),
    
    # Arestas conectadas a N
    ('N', 'K', 60),
    ('N', 'C', 47),
    
    # Arestas conectadas a K
    ('K', 'G', 90),
    ('K', 'E', 10),
    ('K', 'C', 70),
    
    # Arestas conectadas a C
    ('C', 'L', 10),
    ('C', 'E', 10),  # Aresta tracejada na imagem
    ('C', 'K', 30),  # Duplicada, mas mantemos
    
    # Arestas conectadas a E
    ('E', 'G', 40),
    ('E', 'H', 60),
    ('E', 'L', 5),   # Aresta tracejada na imagem
    
    # Arestas conectadas a L
    ('L', 'H', 40),
    
    # Arestas conectadas a H
    ('H', 'G', 80),
    
    # Aresta inferior (F-H)
    ('F', 'H', 55),
    
    # Aresta K-H (no diagrama existe essa conexão)
    ('K', 'H', 73),
]


# ============================================================================
# DADOS DO GRAFO ANTIGO (PARANÁ) - Mantido para referência
# ============================================================================
# Caso queira voltar ao grafo do Paraná, use essas coordenadas
COORDENADAS_CIDADES_PARANA = {
    'Cascavel': (-24.9558, -53.4552),
    'Toledo': (-24.7136, -53.7408),
    'Foz do Iguaçu': (-25.5469, -54.5882),
    'Francisco Beltrão': (-26.0814, -53.0547),
    'São Mateus do Sul': (-25.8728, -50.3828),
    'Paranaguá': (-25.5163, -48.5097),
    'Guarapuava': (-25.3908, -51.4625),
    'Londrina': (-23.3045, -51.1696),
    'Ponta Grossa': (-25.0916, -50.1668),
    'Maringá': (-23.4205, -51.9333),
    'Umuarama': (-23.7661, -53.3250),
    'Curitiba': (-25.4290, -49.2671)
}

ARESTAS_PARANA = [
    ('Maringá', 'Londrina', 114),
    ('Maringá', 'Umuarama', 190),
    ('Umuarama', 'Toledo', 126),
    ('Toledo', 'Cascavel', 50),
    ('Cascavel', 'Foz do Iguaçu', 143),
    ('Cascavel', 'Guarapuava', 250),
    ('Cascavel', 'Francisco Beltrão', 186),
    ('Francisco Beltrão', 'São Mateus do Sul', 354),
    ('Guarapuava', 'Ponta Grossa', 165),
    ('Ponta Grossa', 'Maringá', 314),
    ('Ponta Grossa', 'Londrina', 273),
    ('Ponta Grossa', 'Curitiba', 114),
    ('São Mateus do Sul', 'Curitiba', 157),
    ('Curitiba', 'Paranaguá', 90)
]

# Tabela h(n) em relação a Cascavel (mantida para compatibilidade)
HEURISTICA_PARA_CASCAVEL = {
    'Cascavel': 0,
    'Toledo': 39,
    'Foz do Iguaçu': 131,
    'Francisco Beltrão': 132,
    'São Mateus do Sul': 325,
    'Paranaguá': 501,
    'Guarapuava': 207,
    'Londrina': 296,
    'Ponta Grossa': 332,
    'Maringá': 229,
    'Umuarama': 133,
    'Curitiba': 424
}


def calcular_distancia_manhattan(coord1, coord2):
    """
    Calcula a distância de Manhattan entre duas coordenadas geográficas
    Retorna distância em unidades proporcionais (não km exatos)
    """
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    
    # Distância de Manhattan
    # Para tornar mais realista, multiplicamos por ~111 (km por grau de latitude)
    distancia = abs(lat1 - lat2) + abs(lon1 - lon2)
    
    # Convertendo para uma escala aproximada em km
    # 1 grau de latitude ≈ 111 km
    # 1 grau de longitude no Paraná ≈ 96 km (varia com latitude)
    return round(distancia * 100)  # Fator de escala aproximado

def obter_tabela_heuristica(coords_cidades, destino):
    """
    Calcula a tabela h(n) para todas as cidades em relação a um destino
    usando distância de Manhattan
    """
    coord_destino = coords_cidades[destino]
    heuristica = {}
    
    for cidade, coord in coords_cidades.items():
        heuristica[cidade] = calcular_distancia_manhattan(coord, coord_destino)
    
    return heuristica

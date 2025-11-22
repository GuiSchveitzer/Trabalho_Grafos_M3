"""
Teste simples do Algoritmo Genético para PCV
Executa o AG sem interface gráfica para validação
"""

from grafo import Grafo
from dados import COORDENADAS_CIDADES, ARESTAS
from algoritmo_genetico import AlgoritmoGeneticoPCV


def criar_grafo_trabalho():
    """Cria o grafo do Trabalho 3"""
    grafo = Grafo()
    
    # Adicionar vértices
    for i, (cidade, coords) in enumerate(COORDENADAS_CIDADES.items()):
        grafo.adicionar_vertice(i, nome=cidade, x=coords[0], y=coords[1])
    
    # Criar mapeamento
    cidade_para_id = {cidade: i for i, cidade in enumerate(COORDENADAS_CIDADES.keys())}
    
    # Adicionar arestas
    for cidade1, cidade2, distancia in ARESTAS:
        id1 = cidade_para_id[cidade1]
        id2 = cidade_para_id[cidade2]
        grafo.adicionar_aresta(id1, id2, distancia)
    
    return grafo, cidade_para_id


def main():
    print("=" * 80)
    print("TESTE DO ALGORITMO GENÉTICO - PROBLEMA DO CAIXEIRO VIAJANTE")
    print("=" * 80)
    print()
    
    # Criar grafo
    grafo, cidade_para_id = criar_grafo_trabalho()
    print(f"Grafo criado: {grafo.contar_vertices()} cidades, {grafo.contar_arestas()} arestas")
    print(f"Cidades: {list(COORDENADAS_CIDADES.keys())}")
    print()
    
    # Calcular espaço de busca
    import math
    espaco_busca = math.factorial(grafo.contar_vertices() - 1)
    print(f"Espaço de busca: (n-1)! = {grafo.contar_vertices()-1}! = {espaco_busca} rotas possíveis")
    print()
    
    # Configurar AG
    cidade_inicial = 'F'
    id_inicial = cidade_para_id[cidade_inicial]
    
    print("PARÂMETROS DO ALGORITMO GENÉTICO:")
    print(f"  Cidade Inicial: {cidade_inicial}")
    print(f"  Tamanho da População: 100")
    print(f"  Taxa de Cruzamento: 0.70")
    print(f"  Taxa de Mutação: 0.01")
    print(f"  Pontos de Cruzamento PMX: 2 e 5")
    print(f"  Número de Gerações: 50")
    print()
    
    ag = AlgoritmoGeneticoPCV(
        grafo=grafo,
        cidade_inicial=id_inicial,
        tamanho_populacao=100,
        taxa_cruzamento=0.7,
        taxa_mutacao=0.01,
        ponto1_cruzamento=2,
        ponto2_cruzamento=5,
        intervalo_geracao=0.5
    )
    
    # Callback para mostrar progresso
    def callback_geracao(geracao, ag_inst):
        stats = ag_inst.obter_estatisticas_geracao()
        
        if geracao == 0:
            print("Geração | Melhor Custo | Custo Médio | Rotas Válidas | Diversidade")
            print("-" * 75)
        
        if geracao % 5 == 0 or geracao == 50:
            diversidade = ag_inst.calcular_diversidade()
            print(f"  {geracao:3}   |    {stats['melhor_custo']:6}    |   {stats['custo_medio']:7.2f}   |    {stats['num_rotas_validas']:3}/{ag_inst.tamanho_populacao}    |   {diversidade:7.2f}")
    
    # Executar AG
    print("EXECUTANDO ALGORITMO GENÉTICO...")
    print()
    melhor = ag.executar(max_geracoes=50, callback_geracao=callback_geracao)
    
    print()
    print("=" * 80)
    print("RESULTADO FINAL")
    print("=" * 80)
    print()
    
    rota_completa = melhor.obter_rota_completa()
    nomes = [grafo.obter_nome_vertice(v) for v in rota_completa]
    
    print(f"Melhor Rota Encontrada:")
    print(f"  {' → '.join(nomes)}")
    print()
    print(f"Custo Total: {melhor.custo}")
    print(f"Gerações Executadas: {ag.geracao_atual}")
    print()
    
    # Mostrar top 10
    print("Top 10 Melhores Rotas:")
    print("-" * 80)
    for i, ind in enumerate(ag.obter_melhores_individuos(10), 1):
        rota = ind.obter_rota_completa()
        nomes_rota = [grafo.obter_nome_vertice(v) for v in rota]
        print(f"{i:2}. Custo {ind.custo:5}: {' → '.join(nomes_rota)}")
    print()
    
    # Detalhes dos segmentos
    print("Detalhes dos Segmentos da Melhor Rota:")
    print("-" * 80)
    rota = melhor.obter_rota_completa()
    custo_total = 0
    for i in range(len(rota) - 1):
        cidade_atual = rota[i]
        proxima_cidade = rota[i + 1]
        peso = grafo.obter_peso_aresta(cidade_atual, proxima_cidade)
        nome_atual = grafo.obter_nome_vertice(cidade_atual)
        nome_proxima = grafo.obter_nome_vertice(proxima_cidade)
        
        print(f"  {nome_atual} → {nome_proxima}: {peso} km")
        custo_total += peso if peso else 999999
    
    print()
    print(f"CUSTO TOTAL: {custo_total}")
    print()
    
    # Estatísticas de evolução
    print("Evolução do Algoritmo:")
    print("-" * 80)
    print(f"  Custo Inicial (Geração 0): {ag.historico_melhor_custo[0]}")
    print(f"  Custo Final (Geração {ag.geracao_atual}): {ag.historico_melhor_custo[-1]}")
    print(f"  Melhoria: {ag.historico_melhor_custo[0] - ag.historico_melhor_custo[-1]} ({((ag.historico_melhor_custo[0] - ag.historico_melhor_custo[-1]) / ag.historico_melhor_custo[0] * 100):.2f}%)")
    print()
    
    print("=" * 80)
    print("TESTE CONCLUÍDO COM SUCESSO!")
    print("=" * 80)


if __name__ == "__main__":
    main()

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk

class VisualizadorGrafo:
    """Classe para visualizar grafos usando matplotlib"""
    
    # Paleta de cores para a coloração
    PALETA_CORES = [
        '#FF6B6B',  # Vermelho
        '#4ECDC4',  # Turquesa
        '#A020F0',  # Roxo
        '#FFA07A',  # Salmão
        '#98D8C8',  # Verde menta
        '#F7DC6F',  # Amarelo
        '#BB8FCE',  # Roxo claro
        '#85C1E2',  # Azul céu
        '#F8B195',  # Coral
        '#C7CEEA',  # Lavanda
    ]
    
    def __init__(self, grafo):
        self.grafo = grafo
        self.arrastavel = False
        self.vertice_selecionado = None
        self.artistas_vertices = {}  # Armazena círculos e textos dos vértices
        self.linhas_arestas = []  # Armazena linhas das arestas
        self.textos_arestas = []  # Armazena textos dos pesos
        self.posicoes = {}  # Posições atuais dos vértices
        self.posicoes_personalizadas = None  # Posições personalizadas (do drag and drop)
        
    def desenhar_grafo(self, titulo="Grafo", destacar_arestas=None, cores_vertices=None, mostrar_pesos=True, tamanho_fig=(12, 8), arrastavel=False):
        """
        Desenha o grafo
        """
        # Usar subplots em vez de figure diretamente
        fig, ax = plt.subplots(figsize=tamanho_fig, num=None)  # num=None força nova figura limpa
        
        self.arrastavel = arrastavel
        self.artistas_vertices = {}
        self.linhas_arestas = []
        self.textos_arestas = []
        
        # Posições dos vértices (baseadas nas coordenadas geográficas ou customizadas)
        self.posicoes = {}
        
        if self.posicoes_personalizadas:
            # Usar posições customizadas do drag and drop
            self.posicoes = {k: list(v) for k, v in self.posicoes_personalizadas.items()}
        else:
            # Usar coordenadas geográficas originais
            for id_vertice in self.grafo.obter_todos_vertices():
                pos = self.grafo.obter_posicao_vertice(id_vertice)
                if pos:
                    # Inverter longitude para ajustar visualização (oeste é negativo)
                    # E inverter latitude para que norte fique em cima
                    self.posicoes[id_vertice] = [pos[1], pos[0]]  # Lista mutável para drag
        
        # Desenhar arestas
        for v1, v2, peso in self.grafo.obter_todas_arestas():
            if v1 in self.posicoes and v2 in self.posicoes:
                x1, y1 = self.posicoes[v1]
                x2, y2 = self.posicoes[v2]
                
                # Verifica se esta aresta deve ser destacada
                esta_destacada = False
                if destacar_arestas:
                    esta_destacada = (v1, v2) in destacar_arestas or (v2, v1) in destacar_arestas
                
                if esta_destacada:
                    linha, = ax.plot([x1, x2], [y1, y2], 'r-', linewidth=4, zorder=1, alpha=0.8)
                else:
                    linha, = ax.plot([x1, x2], [y1, y2], 'gray', linewidth=1.5, zorder=1, alpha=0.6)
                
                self.linhas_arestas.append((linha, v1, v2))
                
                # Adicionar peso da aresta
                if mostrar_pesos:
                    meio_x, meio_y = (x1 + x2) / 2, (y1 + y2) / 2
                    texto = ax.text(meio_x, meio_y, str(peso), 
                           bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='gray', alpha=0.8),
                           ha='center', va='center', fontsize=8, zorder=2)
                    self.textos_arestas.append((texto, v1, v2, peso))
        
        # Desenhar vértices
        for id_vertice, pos in self.posicoes.items():
            x, y = pos
            # Determinar cor do vértice
            if cores_vertices and id_vertice in cores_vertices:
                indice_cor = cores_vertices[id_vertice] % len(self.PALETA_CORES)
                cor = self.PALETA_CORES[indice_cor]
            else:
                cor = '#3498db'  # Azul padrão
            
            # Desenhar círculo do vértice
            circulo = plt.Circle((x, y), 0.08, color=cor, ec='black', 
                               linewidth=2, zorder=3, picker=5 if arrastavel else None)
            ax.add_patch(circulo)
            
            # Adicionar nome da cidade
            nome = self.grafo.obter_nome_vertice(id_vertice)
            texto = ax.text(x, y - 0.15, nome, ha='center', va='top', 
                   fontsize=9, fontweight='bold', zorder=4,
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='white', 
                           edgecolor='none', alpha=0.7))
            
            self.artistas_vertices[id_vertice] = {'circulo': circulo, 'texto': texto, 'cor': cor}
        
        # Configurações do gráfico
        ax.set_aspect('equal')
        ax.set_title(titulo, fontsize=16, fontweight='bold', pad=20)
        ax.axis('off')
        
        # Adicionar legenda se houver coloração
        if cores_vertices:
            num_cores = max(cores_vertices.values()) + 1
            elementos_legenda = []
            for i in range(num_cores):
                cor = self.PALETA_CORES[i % len(self.PALETA_CORES)]
                elementos_legenda.append(mpatches.Patch(color=cor, label=f'Cor {i}'))
            ax.legend(handles=elementos_legenda, loc='upper right', fontsize=10)
        
        # Adicionar eventos de drag and drop se solicitado
        if arrastavel:
            self.fig = fig
            self.ax = ax
            fig.canvas.mpl_connect('button_press_event', self.ao_pressionar)
            fig.canvas.mpl_connect('button_release_event', self.ao_soltar)
            fig.canvas.mpl_connect('motion_notify_event', self.ao_mover)
            
            # Adicionar instrução
            ax.text(0.02, 0.98, 'Arraste os vértices para reposicionar', 
                   transform=ax.transAxes, fontsize=10, verticalalignment='top',
                   bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.5))
        
        plt.tight_layout()
        return fig
    
    def ao_pressionar(self, evento):
        """Callback quando o mouse é pressionado"""
        if evento.inaxes != self.ax:
            return
        
        # Encontrar vértice mais próximo
        dist_minima = float('inf')
        vertice_mais_proximo = None
        
        for id_vertice, pos in self.posicoes.items():
            x, y = pos
            dist = ((evento.xdata - x)**2 + (evento.ydata - y)**2)**0.5
            if dist < 0.1 and dist < dist_minima:  # Raio de seleção
                dist_minima = dist
                vertice_mais_proximo = id_vertice
        
        self.vertice_selecionado = vertice_mais_proximo
    
    def ao_soltar(self, evento):
        """Callback quando o mouse é solto"""
        self.vertice_selecionado = None
    
    def ao_mover(self, evento):
        """Callback quando o mouse é movido"""
        if self.vertice_selecionado is None or evento.inaxes != self.ax:
            return
        
        # Atualizar posição do vértice
        self.posicoes[self.vertice_selecionado] = [evento.xdata, evento.ydata]
        
        # Atualizar círculo e texto do vértice
        id_vertice = self.vertice_selecionado
        artista = self.artistas_vertices[id_vertice]
        
        artista['circulo'].center = (evento.xdata, evento.ydata)
        artista['texto'].set_position((evento.xdata, evento.ydata - 0.15))
        
        # Atualizar arestas conectadas
        for linha, v1, v2 in self.linhas_arestas:
            if v1 == id_vertice or v2 == id_vertice:
                x1, y1 = self.posicoes[v1]
                x2, y2 = self.posicoes[v2]
                linha.set_data([x1, x2], [y1, y2])
        
        # Atualizar textos dos pesos
        for texto, v1, v2, peso in self.textos_arestas:
            if v1 == id_vertice or v2 == id_vertice:
                x1, y1 = self.posicoes[v1]
                x2, y2 = self.posicoes[v2]
                meio_x, meio_y = (x1 + x2) / 2, (y1 + y2) / 2
                texto.set_position((meio_x, meio_y))
        
        # Redesenhar
        self.fig.canvas.draw_idle()
    
    def desenhar_em_janela(self, janela, titulo="Grafo", arrastavel=True, **kwargs):
        """
        Desenha o grafo em uma janela Tkinter
        """
        fig = self.desenhar_grafo(titulo=titulo, arrastavel=arrastavel, **kwargs)
        
        canvas = FigureCanvasTkAgg(fig, master=janela)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        return canvas
    
    def mostrar_grafo(self, titulo="Grafo", arrastavel=True, **kwargs):
        """
        Mostra o grafo em uma janela matplotlib interativa
        """
        # Criar o grafo
        self.fig = self.desenhar_grafo(titulo=titulo, arrastavel=arrastavel, **kwargs)
        
        # Mostrar e esperar fechar
        try:
            plt.show(block=True)  # block=True garante que espera fechar
        finally:
            # Garantir que a figura seja fechada após o show
            try:
                if plt.fignum_exists(self.fig.number):
                    plt.close(self.fig)
            except:
                pass

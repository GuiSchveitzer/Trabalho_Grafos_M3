"""
Interface principal do sistema de análise de grafos
Trabalho de Grafos - Paraná
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from grafo import Grafo
from dados import COORDENADAS_CIDADES, ARESTAS, COORDENADAS_CIDADES_PARANA, ARESTAS_PARANA
from planaridade import VerificadorPlanaridade
from welsh_powell import WelshPowell
from a_estrela import AEstrela
from visualizador import VisualizadorGrafo
from algoritmo_genetico import AlgoritmoGeneticoPCV


class GraphApp:
    """Aplicação principal com interface Tkinter"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Análise de Grafos - Trabalho T3 PCV")
        self.root.geometry("1200x800")
        
        # Criar o grafo do trabalho (T3)
        self.grafo = self.criar_grafo_trabalho()
        
        # Variáveis
        self.canvas_atual = None
        self.welsh_powell = None
        self.posicoes_salvas = None  # Posições salvas do drag and drop
        self.visualizador_atual = None  # Visualizador atual para pegar posições
        self.fig_interativa = None  # Figura da janela interativa
        
        # Estado atual para janela interativa
        self.estado_atual = {
            'titulo': 'Grafo',
            'destacar_arestas': None,
            'cores_vertices': None
        }
        
        # Criar interface
        self.criar_interface()
        # Garantir limpeza ao fechar a janela principal
        # Isso força fechamento de figuras matplotlib e widgets embutidos
        try:
            self.root.protocol("WM_DELETE_WINDOW", self.on_fechar)
        except Exception:
            pass
        
    pass
    
    def criar_grafo_trabalho(self):
        """Cria o grafo do Trabalho 3 (PCV com AG)"""
        grafo = Grafo()
        
        # Adicionar vértices (cidades)
        for i, (cidade, coords) in enumerate(COORDENADAS_CIDADES.items()):
            grafo.adicionar_vertice(i, nome=cidade, x=coords[0], y=coords[1])
        
        # Criar mapeamento de nomes para IDs
        cidade_para_id = {cidade: i for i, cidade in enumerate(COORDENADAS_CIDADES.keys())}
        
        # Adicionar arestas
        for cidade1, cidade2, distancia in ARESTAS:
            id1 = cidade_para_id[cidade1]
            id2 = cidade_para_id[cidade2]
            grafo.adicionar_aresta(id1, id2, distancia)
        
        return grafo
    
    def criar_grafo_parana(self):
        """Cria o grafo das cidades do Paraná"""
        grafo = Grafo()
        
        # Adicionar vértices (cidades)
        for i, (cidade, coords) in enumerate(COORDENADAS_CIDADES_PARANA.items()):
            grafo.adicionar_vertice(i, nome=cidade, x=coords[0], y=coords[1])
        
        # Criar mapeamento de nomes para IDs
        cidade_para_id = {cidade: i for i, cidade in enumerate(COORDENADAS_CIDADES_PARANA.keys())}
        
        # Adicionar arestas
        for cidade1, cidade2, distancia in ARESTAS_PARANA:
            id1 = cidade_para_id[cidade1]
            id2 = cidade_para_id[cidade2]
            grafo.adicionar_aresta(id1, id2, distancia)
        
        return grafo
    
    def carregar_grafo_parana(self):
        """Recarrega o grafo do Paraná"""
        self.grafo = self.criar_grafo_parana()
        self.posicoes_salvas = None
        self.welsh_powell = None
        self.atualizar_info_grafo()
        self.atualizar_combos_cidades()
        self.mostrar_grafo_original()
        messagebox.showinfo("Grafo Carregado", "Grafo das cidades do Paraná carregado com sucesso!")
    
    def carregar_grafo_trabalho(self):
        """Recarrega o grafo do Trabalho 3"""
        self.grafo = self.criar_grafo_trabalho()
        self.posicoes_salvas = None
        self.welsh_powell = None
        self.atualizar_info_grafo()
        self.atualizar_combos_cidades()
        self.mostrar_grafo_original()
        messagebox.showinfo("Grafo Carregado", "Grafo do Trabalho 3 (PCV com AG) carregado com sucesso!")
    
    def atualizar_combos_cidades(self):
        """Atualiza os comboboxes de cidades"""
        nomes_vertices = [self.grafo.obter_nome_vertice(v) for v in self.grafo.obter_todos_vertices()]
        self.cidade_inicial['values'] = nomes_vertices
        self.cidade_destino['values'] = nomes_vertices
        self.cidade_inicial_ag['values'] = nomes_vertices
        if nomes_vertices:
            self.cidade_inicial.current(0)
            self.cidade_destino.current(min(1, len(nomes_vertices)-1))
            self.cidade_inicial_ag.current(0)
    
    def criar_grafo_personalizado(self):
        """Abre janela para criar um grafo personalizado"""
        # Criar janela de diálogo
        dialogo = tk.Toplevel(self.root)
        dialogo.title("Criar Grafo Personalizado")
        dialogo.geometry("550x750")
        dialogo.transient(self.root)
        dialogo.grab_set()
        
        # Instruções
        ttk.Label(dialogo, text="Criar Grafo Personalizado", 
                 font=('Arial', 14, 'bold')).pack(pady=10)
        
        instrucoes = """
Formato de entrada:

VÉRTICES (um por linha):
id, nome, latitude, longitude

Exemplo:
0, CidadeA, -25.5, -49.2
1, CidadeB, -23.3, -51.1

ARESTAS (uma por linha):
id_origem, id_destino, peso

Exemplo:
0, 1, 100
1, 2, 150
        """
        
        ttk.Label(dialogo, text=instrucoes, justify=tk.LEFT, 
                 font=('Courier', 9)).pack(padx=10, pady=5)
        
        # Área de texto para vértices
        ttk.Label(dialogo, text="Vértices:", font=('Arial', 10, 'bold')).pack(anchor=tk.W, padx=10)
        texto_vertices = scrolledtext.ScrolledText(dialogo, height=8, width=55)
        texto_vertices.pack(padx=10, pady=5)
        
        # Exemplo pré-preenchido
        texto_vertices.insert('1.0', "0, A, -25.0, -50.0\n1, B, -24.0, -51.0\n2, C, -26.0, -49.0")
        
        # Área de texto para arestas
        ttk.Label(dialogo, text="Arestas:", font=('Arial', 10, 'bold')).pack(anchor=tk.W, padx=10)
        texto_arestas = scrolledtext.ScrolledText(dialogo, height=6, width=55)
        texto_arestas.pack(padx=10, pady=5)
        
        # Exemplo pré-preenchido
        texto_arestas.insert('1.0', "0, 1, 100\n1, 2, 150\n0, 2, 120")
        
        def aplicar_grafo_personalizado():
            try:
                # Criar novo grafo
                novo_grafo = Grafo()
                
                # Processar vértices
                dados_vertices = texto_vertices.get('1.0', tk.END).strip().split('\n')
                mapa_vertices = {}
                
                for linha in dados_vertices:
                    if linha.strip():
                        partes = [p.strip() for p in linha.split(',')]
                        if len(partes) == 4:
                            vid = int(partes[0])
                            nome = partes[1]
                            lat = float(partes[2])
                            lon = float(partes[3])
                            novo_grafo.adicionar_vertice(vid, nome=nome, x=lat, y=lon)
                            mapa_vertices[vid] = nome
                
                # Processar arestas
                dados_arestas = texto_arestas.get('1.0', tk.END).strip().split('\n')
                
                for linha in dados_arestas:
                    if linha.strip():
                        partes = [p.strip() for p in linha.split(',')]
                        if len(partes) == 3:
                            v1 = int(partes[0])
                            v2 = int(partes[1])
                            peso = int(partes[2])
                            novo_grafo.adicionar_aresta(v1, v2, peso)
                
                # Validar grafo
                if novo_grafo.contar_vertices() == 0:
                    messagebox.showerror("Erro", "O grafo deve ter pelo menos um vértice!")
                    return
                
                # Substituir grafo atual
                self.grafo = novo_grafo
                self.posicoes_salvas = None
                self.welsh_powell = None
                
                # Atualizar informações do grafo
                self.atualizar_info_grafo()
                
                # Atualizar combos do A*
                nomes_vertices = [self.grafo.obter_nome_vertice(v) for v in self.grafo.obter_todos_vertices()]
                self.cidade_inicial['values'] = nomes_vertices
                self.cidade_destino['values'] = nomes_vertices
                self.cidade_inicial_ag['values'] = nomes_vertices
                if nomes_vertices:
                    self.cidade_inicial.current(0)
                    self.cidade_destino.current(min(1, len(nomes_vertices)-1))
                    self.cidade_inicial_ag.current(0)
                
                # Mostrar grafo
                self.mostrar_grafo_original()
                
                dialogo.destroy()
                messagebox.showinfo("Sucesso", 
                                  f"Grafo personalizado criado!\n\n" +
                                  f"Vértices: {novo_grafo.contar_vertices()}\n" +
                                  f"Arestas: {novo_grafo.contar_arestas()}")
                
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao criar grafo:\n{str(e)}")
        
        # Botões
        frame_botoes = ttk.Frame(dialogo)
        frame_botoes.pack(pady=10)
        
        ttk.Button(frame_botoes, text="Criar Grafo", 
                  command=aplicar_grafo_personalizado).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_botoes, text="Cancelar", 
                  command=dialogo.destroy).pack(side=tk.LEFT, padx=5)
    
    def criar_interface(self):
        """Cria a interface do usuário"""
        # Frame principal
        frame_principal = ttk.Frame(self.root)
        frame_principal.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Frame esquerdo - Controles
        frame_esquerdo = ttk.Frame(frame_principal, width=300)
        frame_esquerdo.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 10))
        
        # Título
        rotulo_titulo = ttk.Label(frame_esquerdo, text="Análise de Grafos", 
                               font=('Arial', 14, 'bold'))
        rotulo_titulo.pack(pady=10)
        
        # Informações do grafo
        frame_info = ttk.LabelFrame(frame_esquerdo, text="Informações do Grafo", padding=10)
        frame_info.pack(fill=tk.X, pady=5)
        
        self.label_vertices = ttk.Label(frame_info, text=f"Vértices: {self.grafo.contar_vertices()}")
        self.label_vertices.pack(anchor=tk.W)
        self.label_arestas = ttk.Label(frame_info, text=f"Arestas: {self.grafo.contar_arestas()}")
        self.label_arestas.pack(anchor=tk.W)
        
        # Botões de algoritmos
        frame_algoritmos = ttk.LabelFrame(frame_esquerdo, text="Algoritmos", padding=10)
        frame_algoritmos.pack(fill=tk.X, pady=5)
        
        ttk.Button(frame_algoritmos, text="Mostrar Grafo Original", 
                  command=self.mostrar_grafo_original).pack(fill=tk.X, pady=2)
        
        ttk.Button(frame_algoritmos, text="Verificar Planaridade", 
                  command=self.verificar_planaridade).pack(fill=tk.X, pady=2)
        
        ttk.Button(frame_algoritmos, text="Coloração (Welsh-Powell)", 
                  command=self.aplicar_welsh_powell).pack(fill=tk.X, pady=2)
        
        ttk.Separator(frame_algoritmos, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=5)
        
        # ========================================================================
        # ALGORITMO GENÉTICO - PCV (TRABALHO 3)
        # ========================================================================
        ttk.Label(frame_algoritmos, text="Algoritmo Genético (PCV)", 
                 font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(5, 2))
        
        # Cidade de partida/chegada
        ttk.Label(frame_algoritmos, text="Cidade Inicial:").pack(anchor=tk.W)
        self.cidade_inicial_ag = ttk.Combobox(frame_algoritmos, state='readonly')
        self.cidade_inicial_ag['values'] = list(COORDENADAS_CIDADES.keys())
        self.cidade_inicial_ag.current(0)
        self.cidade_inicial_ag.pack(fill=tk.X, pady=2)
        
        # Tamanho da população
        frame_pop = ttk.Frame(frame_algoritmos)
        frame_pop.pack(fill=tk.X, pady=2)
        ttk.Label(frame_pop, text="População:").pack(side=tk.LEFT)
        self.tamanho_populacao = tk.IntVar(value=100)
        spin_pop = ttk.Spinbox(frame_pop, from_=100, to=500, textvariable=self.tamanho_populacao, width=10)
        spin_pop.pack(side=tk.RIGHT)
        
        # Taxa de cruzamento
        frame_cruz = ttk.Frame(frame_algoritmos)
        frame_cruz.pack(fill=tk.X, pady=2)
        ttk.Label(frame_cruz, text="Taxa Cruzamento:").pack(side=tk.LEFT)
        self.taxa_cruzamento = tk.DoubleVar(value=0.7)
        spin_cruz = ttk.Spinbox(frame_cruz, from_=0.6, to=0.8, increment=0.05, 
                                textvariable=self.taxa_cruzamento, width=10)
        spin_cruz.pack(side=tk.RIGHT)
        
        # Taxa de mutação
        frame_mut = ttk.Frame(frame_algoritmos)
        frame_mut.pack(fill=tk.X, pady=2)
        ttk.Label(frame_mut, text="Taxa Mutação:").pack(side=tk.LEFT)
        self.taxa_mutacao = tk.DoubleVar(value=0.01)
        spin_mut = ttk.Spinbox(frame_mut, from_=0.005, to=0.02, increment=0.001, 
                               textvariable=self.taxa_mutacao, width=10)
        spin_mut.pack(side=tk.RIGHT)
        
        # Número de gerações
        frame_ger = ttk.Frame(frame_algoritmos)
        frame_ger.pack(fill=tk.X, pady=2)
        ttk.Label(frame_ger, text="Gerações:").pack(side=tk.LEFT)
        self.num_geracoes = tk.IntVar(value=20)
        spin_ger = ttk.Spinbox(frame_ger, from_=20, to=200, increment=10, 
                               textvariable=self.num_geracoes, width=10)
        spin_ger.pack(side=tk.RIGHT)
        
        ttk.Button(frame_algoritmos, text="Executar AG para PCV", 
                  command=self.executar_algoritmo_genetico).pack(fill=tk.X, pady=2)
        
        ttk.Separator(frame_algoritmos, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=5)
        
        # A* - Seleção de cidades
        ttk.Label(frame_algoritmos, text="Algoritmo A*", 
                 font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(5, 2))
        
        # Cidade origem
        ttk.Label(frame_algoritmos, text="Origem:").pack(anchor=tk.W)
        self.cidade_inicial = ttk.Combobox(frame_algoritmos, state='readonly')
        self.cidade_inicial['values'] = list(COORDENADAS_CIDADES.keys())
        self.cidade_inicial.current(0)
        self.cidade_inicial.pack(fill=tk.X, pady=2)
        
        # Cidade destino
        ttk.Label(frame_algoritmos, text="Destino:").pack(anchor=tk.W)
        self.cidade_destino = ttk.Combobox(frame_algoritmos, state='readonly')
        self.cidade_destino['values'] = list(COORDENADAS_CIDADES.keys())
        self.cidade_destino.current(6)  # Guarapuava como padrão
        self.cidade_destino.pack(fill=tk.X, pady=2)
        
        ttk.Button(frame_algoritmos, text="Encontrar Caminho Mínimo (A*)", 
                  command=self.aplicar_a_estrela).pack(fill=tk.X, pady=2)
        
        ttk.Separator(frame_algoritmos, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=5)
        
        # Opção para criar grafo personalizado
        ttk.Label(frame_algoritmos, text="Troca de Grafo", 
                 font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(5, 2))
        ttk.Button(frame_algoritmos, text="Carregar Grafo do Trabalho 3", 
                  command=self.carregar_grafo_trabalho).pack(fill=tk.X, pady=2)
        ttk.Button(frame_algoritmos, text="Voltar para Grafo do Paraná", 
                  command=self.carregar_grafo_parana).pack(fill=tk.X, pady=2)
        ttk.Button(frame_algoritmos, text="Criar Novo Grafo Personalizado", 
                  command=self.criar_grafo_personalizado).pack(fill=tk.X, pady=2)
        
        ttk.Separator(frame_algoritmos, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=5)
        
        # Botão para janela interativa
        ttk.Label(frame_algoritmos, text="Modo Interativo", 
                 font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(5, 2))
        ttk.Button(frame_algoritmos, text="Abrir Grafo Interativo (Drag & Drop)", 
                  command=self.abrir_janela_interativa).pack(fill=tk.X, pady=2)
        
        # Frame de layout personalizado (MOVIDO PARA CIMA)
        frame_layout = ttk.LabelFrame(frame_esquerdo, text="Layout Personalizado", padding=5)
        frame_layout.pack(fill=tk.X, pady=5)
        
        ttk.Button(frame_layout, text="Salvar Layout Atual", 
                  command=self.salvar_layout_personalizado).pack(fill=tk.X, pady=2)
        ttk.Button(frame_layout, text="Resetar para Original", 
                  command=self.resetar_layout).pack(fill=tk.X, pady=2)
        
        # Área de resultados (NO FINAL)
        frame_resultados = ttk.LabelFrame(frame_esquerdo, text="Resultados", padding=10)
        frame_resultados.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.texto_resultados = scrolledtext.ScrolledText(frame_resultados, wrap=tk.WORD, 
                                                       height=10, width=35)
        self.texto_resultados.pack(fill=tk.BOTH, expand=True)
        
        # Frame direito - Visualização
        self.frame_viz = ttk.Frame(frame_principal)
        self.frame_viz.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Mostrar grafo original inicialmente
        self.atualizar_combos_cidades()
        self.mostrar_grafo_original()
    
    def atualizar_info_grafo(self):
        """Atualiza as informações do grafo na interface"""
        self.label_vertices.config(text=f"Vértices: {self.grafo.contar_vertices()}")
        self.label_arestas.config(text=f"Arestas: {self.grafo.contar_arestas()}")
    
    def mostrar_grafo_original(self):
        """Mostra o grafo original"""
        self.limpar_canvas()
        
        # Atualizar estado atual
        self.estado_atual = {
            'titulo': 'Grafo do Trabalho 3 - PCV com AG',
            'destacar_arestas': None,
            'cores_vertices': None
        }
        
        visualizador = VisualizadorGrafo(self.grafo)
        
        # Aplicar posições salvas se existirem
        if self.posicoes_salvas:
            visualizador.posicoes_personalizadas = self.posicoes_salvas.copy()
        
        fig = visualizador.desenhar_grafo(titulo="Grafo do Trabalho 3 - PCV com AG", tamanho_fig=(10, 8), arrastavel=False)
        
        self.canvas_atual = FigureCanvasTkAgg(fig, master=self.frame_viz)
        self.canvas_atual.draw()
        self.canvas_atual.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        info_layout = " (Layout personalizado)" if self.posicoes_salvas else ""
        self.atualizar_resultados(f"Grafo original exibido{info_layout}.\n\nUse o botão 'Abrir Grafo Interativo' para arrastar vértices.\n\n" + str(self.grafo))
    
    def verificar_planaridade(self):
        """Verifica planaridade do grafo"""
        verificador = VerificadorPlanaridade(self.grafo)
        eh_planar, razao = verificador.verificar_planaridade()
        euler = verificador.obter_caracteristica_euler()
        
        resultado = "=" * 50 + "\n"
        resultado += "VERIFICAÇÃO DE PLANARIDADE\n"
        resultado += "=" * 50 + "\n\n"
        
        resultado += f"Vértices (V): {euler['vertices']}\n"
        resultado += f"Arestas (E): {euler['arestas']}\n"
        resultado += f"Faces estimadas (F): {euler['faces']}\n"
        resultado += f"Característica de Euler (V-E+F): {euler['caracteristica_euler']}\n\n"
        
        if eh_planar:
            resultado += "O GRAFO É PLANAR\n"
        else:
            resultado += "O GRAFO NÃO É PLANAR\n"
        
        resultado += f"\nRazão: {razao}\n"
        
        self.atualizar_resultados(resultado)
        
        # Mostrar mensagem
        if eh_planar:
            messagebox.showinfo("Planaridade", f"O grafo É PLANAR!\n\n{razao}")
        else:
            messagebox.showwarning("Planaridade", f"O grafo NÃO É PLANAR!\n\n{razao}")
    
    def aplicar_welsh_powell(self):
        """Aplica o algoritmo Welsh-Powell com visualização passo a passo"""
        self.limpar_canvas()
        
        self.welsh_powell = WelshPowell(self.grafo)
        cores = self.welsh_powell.color_graph(registrar_passos=True)
        passos = self.welsh_powell.obter_passos()
        estatisticas = self.welsh_powell.get_statistics()
        
        # Criar janela de visualização passo a passo
        self.mostrar_passos_welsh_powell(passos, cores, estatisticas)
    
    def mostrar_passos_welsh_powell(self, passos, cores_finais, estatisticas):
        """Mostra os passos do Welsh-Powell em uma janela interativa"""
        janela_passos = tk.Toplevel(self.root)
        janela_passos.title("Welsh-Powell - Passo a Passo")
        # Janela maior para melhor visualização
        janela_passos.geometry("1200x900")
        
        # Variável para controlar o passo atual
        passo_atual = tk.IntVar(value=0)
        
        # Frame superior com informações do passo
        frame_info = ttk.Frame(janela_passos)
        frame_info.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(frame_info, text="Algoritmo Welsh-Powell - Visualização Passo a Passo", 
                 font=('Arial', 14, 'bold')).pack()
        
        label_passo = ttk.Label(frame_info, text="", font=('Arial', 10))
        label_passo.pack(pady=5)
        
        # Frame para descrição detalhada
        frame_desc = ttk.LabelFrame(janela_passos, text="Detalhes do Passo", padding=10)
        frame_desc.pack(fill=tk.X, padx=10, pady=5)
        
        texto_desc = scrolledtext.ScrolledText(frame_desc, height=6, width=80, wrap=tk.WORD)
        texto_desc.pack(fill=tk.BOTH, expand=True)
        
        # Frame para visualização do grafo
        frame_viz = ttk.Frame(janela_passos)
        frame_viz.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Frame inferior com controles
        frame_controles = ttk.Frame(janela_passos)
        frame_controles.pack(fill=tk.X, padx=10, pady=10)
        
        def atualizar_visualizacao():
            """Atualiza a visualização para o passo atual"""
            idx = passo_atual.get()
            passo = passos[idx]
            
            # Atualizar label do passo
            label_passo.config(text=f"Passo {idx + 1} de {len(passos)}")
            
            # Atualizar descrição
            texto_desc.delete('1.0', tk.END)
            texto_desc.insert('1.0', passo['descricao'] + "\n\n")
            
            if passo['tipo'] == 'ordenacao':
                texto_desc.insert(tk.END, "Vértices ordenados por grau (decrescente):\n")
                for v in passo['vertices_ordenados']:
                    nome = self.grafo.obter_nome_vertice(v)
                    grau = passo['graus'][v]
                    texto_desc.insert(tk.END, f"  • {nome}: grau {grau}\n")
            
            elif passo['tipo'] == 'coloracao_grupo':
                texto_desc.insert(tk.END, f"Cor {passo['cor_atual']} associada aos vértices:\n\n")
                
                for nome in passo['nomes_vertices']:
                    texto_desc.insert(tk.END, f"  ✓ {nome}\n")
                
                texto_desc.insert(tk.END, f"\nTotal: {len(passo['vertices_coloridos'])} vértice(s)\n")
                texto_desc.insert(tk.END, "\nEstes vértices NÃO são adjacentes entre si,\n")
                texto_desc.insert(tk.END, "portanto podem ter a mesma cor.")
            
            # Limpar e redesenhar grafo
            for widget in frame_viz.winfo_children():
                widget.destroy()
            
            visualizador = VisualizadorGrafo(self.grafo)
            
            # Aplicar posições salvas se existirem
            if self.posicoes_salvas:
                visualizador.posicoes_personalizadas = self.posicoes_salvas.copy()
            
            fig = visualizador.desenhar_grafo(
                titulo=f"Passo {idx + 1}: {passo['descricao']}",
                cores_vertices=passo['cores_atuais'] if passo['cores_atuais'] else None,
                # Voltar ao tamanho de figura original (apenas janela aumentada)
                tamanho_fig=(8, 6),
                arrastavel=False
            )
            
            canvas = FigureCanvasTkAgg(fig, master=frame_viz)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
            # Atualizar estado dos botões
            btn_anterior.config(state=tk.NORMAL if idx > 0 else tk.DISABLED)
            btn_proximo.config(state=tk.NORMAL if idx < len(passos) - 1 else tk.DISABLED)
        
        def proximo_passo():
            if passo_atual.get() < len(passos) - 1:
                passo_atual.set(passo_atual.get() + 1)
                atualizar_visualizacao()
        
        def passo_anterior():
            if passo_atual.get() > 0:
                passo_atual.set(passo_atual.get() - 1)
                atualizar_visualizacao()
        
        def finalizar():
            """Mostra resultado final no canvas principal"""
            janela_passos.destroy()
            
            # Atualizar estado atual
            self.estado_atual = {
                'titulo': 'Coloração de Grafo - Welsh-Powell',
                'destacar_arestas': None,
                'cores_vertices': cores_finais
            }
            
            # Visualizar grafo colorido no canvas principal
            visualizador = VisualizadorGrafo(self.grafo)
            
            if self.posicoes_salvas:
                visualizador.posicoes_personalizadas = self.posicoes_salvas.copy()
            
            fig = visualizador.desenhar_grafo(
                titulo="Coloração de Grafo - Welsh-Powell",
                cores_vertices=cores_finais,
                # Voltar ao tamanho de figura original
                tamanho_fig=(10, 8),
                arrastavel=False
            )
            
            self.canvas_atual = FigureCanvasTkAgg(fig, master=self.frame_viz)
            self.canvas_atual.draw()
            self.canvas_atual.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
            # Mostrar resultados
            resultado = "=" * 50 + "\n"
            resultado += "COLORAÇÃO DE GRAFO (WELSH-POWELL)\n"
            resultado += "=" * 50 + "\n\n"
            
            resultado += f"Número Cromático: {estatisticas['chromatic_number']}\n"
            resultado += f"Cores utilizadas: {estatisticas['chromatic_number']}\n\n"
            
            resultado += "Distribuição de cores:\n"
            for nome_cor, contagem in estatisticas['color_distribution'].items():
                resultado += f"  {nome_cor}: {contagem} vértices\n"
            
            resultado += f"\n{estatisticas['validation_message']}\n\n"
            
            resultado += "Coloração por cidade:\n"
            classes_cores = self.welsh_powell.get_color_classes()
            for cor, vertices in sorted(classes_cores.items()):
                nomes_cidades = [self.grafo.obter_nome_vertice(v) for v in vertices]
                resultado += f"  Cor {cor}: {', '.join(nomes_cidades)}\n"
            
            self.atualizar_resultados(resultado)
            
            messagebox.showinfo("Welsh-Powell", 
                              f"Coloração concluída!\n\nNúmero Cromático: {estatisticas['chromatic_number']}")
        
        # Botões de controle
        btn_anterior = ttk.Button(frame_controles, text="← Anterior", command=passo_anterior)
        btn_anterior.pack(side=tk.LEFT, padx=5)
        
        btn_proximo = ttk.Button(frame_controles, text="Próximo →", command=proximo_passo)
        btn_proximo.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(frame_controles, text="Finalizar e Ver Resultado", 
                  command=finalizar).pack(side=tk.RIGHT, padx=5)
        
        # Mostrar primeiro passo
        atualizar_visualizacao()

    
    def aplicar_a_estrela(self):
        """Aplica o algoritmo A*"""
        nome_cidade_inicial = self.cidade_inicial.get()
        nome_cidade_destino = self.cidade_destino.get()
        
        if nome_cidade_inicial == nome_cidade_destino:
            messagebox.showwarning("A*", "Origem e destino devem ser diferentes!")
            return
        
        # Encontrar IDs das cidades
        cidade_para_id = {self.grafo.obter_nome_vertice(i): i 
                      for i in self.grafo.obter_todos_vertices()}
        
        id_inicial = cidade_para_id[nome_cidade_inicial]
        id_destino = cidade_para_id[nome_cidade_destino]
        
        # Executar A*
        a_estrela = AEstrela(self.grafo)
        caminho, custo = a_estrela.encontrar_caminho(id_inicial, id_destino)
        
        if caminho is None:
            messagebox.showerror("A*", "Não foi possível encontrar um caminho!")
            return
        
        # Visualizar caminho
        self.limpar_canvas()
        
        arestas_caminho = a_estrela.obter_arestas_caminho()
        
        # Atualizar estado atual
        self.estado_atual = {
            'titulo': f"Caminho Mínimo: {nome_cidade_inicial} → {nome_cidade_destino}",
            'destacar_arestas': arestas_caminho,
            'cores_vertices': None
        }
        
        visualizador = VisualizadorGrafo(self.grafo)
        
        # Aplicar posições salvas se existirem
        if self.posicoes_salvas:
            visualizador.posicoes_personalizadas = self.posicoes_salvas.copy()
        
        fig = visualizador.desenhar_grafo(
            titulo=f"Caminho Mínimo: {nome_cidade_inicial} → {nome_cidade_destino}",
            destacar_arestas=arestas_caminho,
            tamanho_fig=(10, 8),
            arrastavel=False
        )
        
        self.canvas_atual = FigureCanvasTkAgg(fig, master=self.frame_viz)
        self.canvas_atual.draw()
        self.canvas_atual.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Mostrar resultados
        detalhes = a_estrela.obter_detalhes_caminho()
        
        resultado = "=" * 50 + "\n"
        resultado += "ALGORITMO A* - CAMINHO MÍNIMO\n"
        resultado += "=" * 50 + "\n\n"
        
        resultado += f"Origem: {nome_cidade_inicial}\n"
        resultado += f"Destino: {nome_cidade_destino}\n"
        resultado += f"Distância Total: {custo} km\n"
        resultado += f"Número de cidades no caminho: {detalhes['num_vertices']}\n\n"
        
        resultado += "Caminho:\n"
        resultado += " → ".join(detalhes['caminho']) + "\n\n"
        
        resultado += "Segmentos:\n"
        for i, aresta in enumerate(detalhes['arestas'], 1):
            resultado += f"  {i}. {aresta['de']} → {aresta['para']}: {aresta['distancia']} km\n"
        
        resultado += f"\n{'='*50}\n"
        
        # Tabela heurística
        resultado += "\nTabela h(n) - Distância de Manhattan para o destino:\n"
        tabela_heuristica = a_estrela.calcular_tabela_heuristica(id_destino)
        for cidade, valor_h in sorted(tabela_heuristica.items(), key=lambda x: x[1]):
            resultado += f"  {cidade}: {valor_h}\n"
        
        self.atualizar_resultados(resultado)
        
        messagebox.showinfo("A*", 
                          f"Caminho encontrado!\n\nDistância: {custo} km\nCidades: {detalhes['num_vertices']}")
    
    def executar_algoritmo_genetico(self):
        """Executa o Algoritmo Genético para resolver o PCV"""
        nome_cidade_inicial = self.cidade_inicial_ag.get()
        
        # Encontrar ID da cidade
        cidade_para_id = {self.grafo.obter_nome_vertice(i): i 
                          for i in self.grafo.obter_todos_vertices()}
        
        id_inicial = cidade_para_id[nome_cidade_inicial]
        
        # Obter parâmetros
        tamanho_pop = self.tamanho_populacao.get()
        taxa_cruz = self.taxa_cruzamento.get()
        taxa_mut = self.taxa_mutacao.get()
        num_ger = self.num_geracoes.get()
        
        # Criar instância do AG
        ag = AlgoritmoGeneticoPCV(
            grafo=self.grafo,
            cidade_inicial=id_inicial,
            tamanho_populacao=tamanho_pop,
            taxa_cruzamento=taxa_cruz,
            taxa_mutacao=taxa_mut,
            ponto1_cruzamento=2,
            ponto2_cruzamento=5,
            intervalo_geracao=0.5
        )
        
        # Mostrar janela de visualização
        self.mostrar_evolucao_ag(ag, num_ger, nome_cidade_inicial)
    
    def mostrar_evolucao_ag(self, ag: AlgoritmoGeneticoPCV, max_geracoes: int, cidade_inicial: str):
        """Mostra a evolução do AG em uma janela interativa"""
        janela_ag = tk.Toplevel(self.root)
        janela_ag.title("Algoritmo Genético - PCV")
        janela_ag.geometry("1300x900")
        
        # Variável para controlar a geração atual
        geracao_atual = tk.IntVar(value=0)
        ag_executando = tk.BooleanVar(value=False)
        pausado_para_visualizacao = tk.BooleanVar(value=False)
        
        # Frame superior com informações
        frame_info = ttk.Frame(janela_ag)
        frame_info.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(frame_info, text=f"Algoritmo Genético - Cidade Inicial: {cidade_inicial}", 
                 font=('Arial', 14, 'bold')).pack()
        
        label_geracao = ttk.Label(frame_info, text="Geração: 0", font=('Arial', 11))
        label_geracao.pack(pady=5)
        
        label_melhor = ttk.Label(frame_info, text="Melhor Custo: -", font=('Arial', 10))
        label_melhor.pack()
        
        label_medio = ttk.Label(frame_info, text="Custo Médio: -", font=('Arial', 10))
        label_medio.pack()
        
        # Frame para gráfico de evolução
        frame_grafico = ttk.LabelFrame(janela_ag, text="Evolução do Custo", padding=5)
        frame_grafico.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Frame para detalhes
        frame_detalhes = ttk.LabelFrame(janela_ag, text="Melhores Rotas da Geração", padding=5)
        frame_detalhes.pack(fill=tk.X, padx=10, pady=5)
        
        texto_detalhes = scrolledtext.ScrolledText(frame_detalhes, height=8, width=120, wrap=tk.WORD)
        texto_detalhes.pack(fill=tk.BOTH, expand=True)
        
        # Frame de controles
        frame_controles = ttk.Frame(janela_ag)
        frame_controles.pack(fill=tk.X, padx=10, pady=10)
        
        # Variável para saber se usuário quer ver população
        mostrar_pop_var = tk.BooleanVar(value=False)
        
        def callback_geracao(ger, ag_inst):
            """Chamado após cada geração"""
            # Atualizar labels
            stats = ag_inst.obter_estatisticas_geracao()
            label_geracao.config(text=f"Geração: {ger} / {max_geracoes}")
            label_melhor.config(text=f"Melhor Custo: {stats['melhor_custo']}")
            label_medio.config(text=f"Custo Médio: {stats['custo_medio']:.2f}")
            
            # Atualizar gráfico
            atualizar_grafico_evolucao()
            
            # Perguntar se quer ver a população (a cada 5 gerações ou se for a última)
            if ger > 0 and (ger % 5 == 0 or ger == max_geracoes):
                resposta = messagebox.askyesno(
                    "Visualizar População?",
                    f"Geração {ger} concluída!\n\n"
                    f"Melhor custo: {stats['melhor_custo']}\n"
                    f"Custo médio: {stats['custo_medio']:.2f}\n"
                    f"Rotas válidas: {stats['num_rotas_validas']}/{ag_inst.tamanho_populacao}\n\n"
                    f"Deseja ver os 10 melhores indivíduos desta geração?",
                    parent=janela_ag
                )
                
                if resposta:
                    mostrar_top_10(stats['top_10'])
                    
                    # Pausar execução até o usuário clicar em continuar
                    pausado_para_visualizacao.set(True)
                    btn_continuar_visualizacao.config(state=tk.NORMAL)
                    
                    # Aguardar usuário clicar em continuar
                    janela_ag.wait_variable(pausado_para_visualizacao)
                    btn_continuar_visualizacao.config(state=tk.DISABLED)
            
            # Atualizar janela
            janela_ag.update()
        
        def mostrar_top_10(top_10):
            """Mostra os 10 melhores indivíduos"""
            texto_detalhes.delete('1.0', tk.END)
            texto_detalhes.insert('1.0', f"Top 10 Melhores Rotas da Geração {ag.geracao_atual}:\n\n")
            
            for i, ind in enumerate(top_10, 1):
                rota_completa = ind.obter_rota_completa()
                nomes = [self.grafo.obter_nome_vertice(v) for v in rota_completa]
                texto_detalhes.insert(tk.END, f"{i:2}. {' → '.join(nomes)}\n")
                texto_detalhes.insert(tk.END, f"    Custo: {ind.custo}\n\n")
            
            # Adicionar instrução
            texto_detalhes.insert(tk.END, "\n" + "="*80 + "\n")
            texto_detalhes.insert(tk.END, "Clique no botão 'Continuar Execução' abaixo quando terminar de visualizar.\n")
            
            # Forçar atualização da interface
            janela_ag.update()
        
        def atualizar_grafico_evolucao():
            """Atualiza o gráfico de evolução"""
            for widget in frame_grafico.winfo_children():
                widget.destroy()
            
            if len(ag.historico_melhor_custo) == 0:
                return
            
            fig, ax = plt.subplots(figsize=(11, 4))
            
            geracoes = list(range(len(ag.historico_melhor_custo)))
            ax.plot(geracoes, ag.historico_melhor_custo, 'b-', linewidth=2, label='Melhor Custo')
            ax.plot(geracoes, ag.historico_custo_medio, 'r--', linewidth=1.5, label='Custo Médio')
            
            ax.set_xlabel('Geração', fontsize=10)
            ax.set_ylabel('Custo', fontsize=10)
            ax.set_title('Evolução do Algoritmo Genético', fontsize=12, fontweight='bold')
            ax.legend()
            ax.grid(True, alpha=0.3)
            
            canvas = FigureCanvasTkAgg(fig, master=frame_grafico)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        def executar_ag():
            """Executa o AG"""
            ag_executando.set(True)
            btn_executar.config(state=tk.DISABLED)
            btn_continuar.config(state=tk.DISABLED)
            
            # Executar AG
            melhor = ag.executar(max_geracoes=max_geracoes, callback_geracao=callback_geracao)
            
            # Mostrar resultado final
            mostrar_resultado_final(melhor)
            
            ag_executando.set(False)
            btn_executar.config(state=tk.DISABLED)
            btn_continuar.config(state=tk.NORMAL)
        
        def continuar_execucao():
            """Continua a execução por mais gerações"""
            resposta = tk.simpledialog.askinteger(
                "Continuar Execução",
                "Quantas gerações adicionais?",
                initialvalue=20,
                minvalue=1,
                maxvalue=500,
                parent=janela_ag
            )
            
            if resposta:
                ag_executando.set(True)
                btn_continuar.config(state=tk.DISABLED)
                
                # Continuar por mais N gerações
                for _ in range(resposta):
                    ag.evoluir_geracao()
                    callback_geracao(ag.geracao_atual, ag)
                
                # Mostrar novo resultado
                mostrar_resultado_final(ag.melhor_individuo)
                
                ag_executando.set(False)
                btn_continuar.config(state=tk.NORMAL)
        
        def mostrar_resultado_final(melhor_ind):
            """Mostra o resultado final graficamente"""
            # Atualizar área de texto
            texto_detalhes.delete('1.0', tk.END)
            texto_detalhes.insert('1.0', "=" * 80 + "\n")
            texto_detalhes.insert(tk.END, "RESULTADO FINAL DO ALGORITMO GENÉTICO\n")
            texto_detalhes.insert(tk.END, "=" * 80 + "\n\n")
            
            rota_completa = melhor_ind.obter_rota_completa()
            nomes = [self.grafo.obter_nome_vertice(v) for v in rota_completa]
            
            texto_detalhes.insert(tk.END, f"Melhor Rota Encontrada:\n")
            texto_detalhes.insert(tk.END, f"  {' → '.join(nomes)}\n\n")
            texto_detalhes.insert(tk.END, f"Custo Total: {melhor_ind.custo}\n")
            texto_detalhes.insert(tk.END, f"Gerações Executadas: {ag.geracao_atual}\n\n")
            
            texto_detalhes.insert(tk.END, "Top 10 Melhores Rotas Finais:\n\n")
            for i, ind in enumerate(ag.obter_melhores_individuos(10), 1):
                rota = ind.obter_rota_completa()
                nomes_rota = [self.grafo.obter_nome_vertice(v) for v in rota]
                texto_detalhes.insert(tk.END, f"{i:2}. Custo {ind.custo}: {' → '.join(nomes_rota)}\n")
            
            # Visualizar no canvas principal
            visualizar_melhor_rota(melhor_ind)
            
            messagebox.showinfo(
                "AG Concluído",
                f"Algoritmo Genético concluído!\n\n"
                f"Melhor custo encontrado: {melhor_ind.custo}\n"
                f"Gerações executadas: {ag.geracao_atual}\n\n"
                f"A melhor rota foi visualizada no canvas principal.",
                parent=janela_ag
            )
        
        def visualizar_melhor_rota(melhor_ind):
            """Visualiza a melhor rota no canvas principal"""
            self.limpar_canvas()
            
            # Obter arestas da rota
            rota_completa = melhor_ind.obter_rota_completa()
            arestas_rota = []
            for i in range(len(rota_completa) - 1):
                arestas_rota.append((rota_completa[i], rota_completa[i+1]))
            
            # Atualizar estado atual
            self.estado_atual = {
                'titulo': f"Melhor Rota PCV (AG) - Custo: {melhor_ind.custo}",
                'destacar_arestas': arestas_rota,
                'cores_vertices': None
            }
            
            visualizador = VisualizadorGrafo(self.grafo)
            
            if self.posicoes_salvas:
                visualizador.posicoes_personalizadas = self.posicoes_salvas.copy()
            
            fig = visualizador.desenhar_grafo(
                titulo=f"Melhor Rota PCV (AG) - Custo: {melhor_ind.custo}",
                destacar_arestas=arestas_rota,
                tamanho_fig=(10, 8),
                arrastavel=False
            )
            
            self.canvas_atual = FigureCanvasTkAgg(fig, master=self.frame_viz)
            self.canvas_atual.draw()
            self.canvas_atual.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
            # Atualizar resultados
            rota_nomes = [self.grafo.obter_nome_vertice(v) for v in rota_completa]
            resultado = "=" * 50 + "\n"
            resultado += "ALGORITMO GENÉTICO - PCV\n"
            resultado += "=" * 50 + "\n\n"
            resultado += f"Cidade Inicial: {self.grafo.obter_nome_vertice(melhor_ind.cidade_inicial)}\n"
            resultado += f"Custo Total: {melhor_ind.custo}\n"
            resultado += f"Gerações: {ag.geracao_atual}\n\n"
            resultado += "Melhor Rota:\n"
            resultado += " → ".join(rota_nomes) + "\n\n"
            
            resultado += f"Parâmetros do AG:\n"
            resultado += f"  População: {ag.tamanho_populacao}\n"
            resultado += f"  Taxa Cruzamento: {ag.taxa_cruzamento}\n"
            resultado += f"  Taxa Mutação: {ag.taxa_mutacao}\n"
            resultado += f"  Intervalo Geração: {ag.intervalo_geracao}\n"
            
            self.atualizar_resultados(resultado)
        
        def continuar_apos_visualizacao():
            """Libera a execução após visualizar população"""
            pausado_para_visualizacao.set(False)
        
        # Botões de controle
        btn_executar = ttk.Button(frame_controles, text="Executar AG", command=executar_ag)
        btn_executar.pack(side=tk.LEFT, padx=5)
        
        btn_continuar_visualizacao = ttk.Button(frame_controles, text="Continuar Execução Após Visualizar", 
                                                command=continuar_apos_visualizacao, state=tk.DISABLED)
        btn_continuar_visualizacao.pack(side=tk.LEFT, padx=5)
        
        btn_continuar = ttk.Button(frame_controles, text="Continuar Execução", 
                                   command=continuar_execucao, state=tk.DISABLED)
        btn_continuar.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(frame_controles, text="Fechar", 
                  command=janela_ag.destroy).pack(side=tk.RIGHT, padx=5)
    
    def abrir_janela_interativa(self):
        """Abre uma janela matplotlib interativa com drag and drop"""
        # Isso garante que não há duplicação
        try:
            plt.close('all')  # Fecha absolutamente todas as figuras
        except:
            pass
        
        # Pequena pausa para garantir que fechou
        self.root.update()  # Atualiza a janela tkinter
        
        # Criar novo visualizador
        visualizador = VisualizadorGrafo(self.grafo)
        self.visualizador_atual = visualizador  # Guardar referência
        
        # Aplicar posições salvas se existirem
        if self.posicoes_salvas:
            visualizador.posicoes_personalizadas = self.posicoes_salvas.copy()
        
        # Usar o estado atual
        titulo = "Interativo - " + self.estado_atual['titulo']
        destacar_arestas = self.estado_atual['destacar_arestas']
        cores_vertices = self.estado_atual['cores_vertices']
        
        messagebox.showinfo("Modo Interativo", 
                          "Uma janela interativa será aberta!\n\n" +
                          "Clique e arraste os vértices para movê-los\n" +
                          "As arestas se ajustam automaticamente\n" +
                          "Use 'Salvar Layout Atual' depois de fechar\n\n" +
                          "Feche a janela quando terminar.")
        
        # Criar e mostrar o grafo
        visualizador.mostrar_grafo(titulo=titulo, 
                            destacar_arestas=destacar_arestas,
                            cores_vertices=cores_vertices,
                            arrastavel=True,
                            tamanho_fig=(12, 9))
        
        # Guardar referência da figura
        if hasattr(visualizador, 'fig'):
            self.fig_interativa = visualizador.fig
        
        self.atualizar_resultados("Janela interativa fechada.\n\nClique em 'Salvar Layout Atual' para manter as posições!")
    
    def salvar_layout_personalizado(self):
        """Salva o layout personalizado do drag and drop"""
        if self.visualizador_atual and hasattr(self.visualizador_atual, 'posicoes') and self.visualizador_atual.posicoes:
            self.posicoes_salvas = self.visualizador_atual.posicoes.copy()
            
            messagebox.showinfo("Layout Salvo", 
                              "Layout personalizado salvo com sucesso!\n\n" +
                              "Todas as visualizações agora usarão este layout.\n" +
                              "Use 'Resetar para Original' para voltar às coordenadas geográficas.")
            
            # Atualizar visualização atual
            self.mostrar_grafo_original()
        else:
            messagebox.showwarning("Aviso", 
                                 "Nenhum layout para salvar!\n\n" +
                                 "Primeiro abra a janela interativa e mova os vértices.")
    
    def resetar_layout(self):
        """Reseta para o layout original (coordenadas geográficas)"""
        if self.posicoes_salvas:
            self.posicoes_salvas = None
            self.visualizador_atual = None
            
            messagebox.showinfo("Layout Resetado", 
                              "Layout resetado para coordenadas geográficas originais!")
            
            # Atualizar visualização atual
            self.mostrar_grafo_original()
        else:
            messagebox.showinfo("Info", "O layout já está usando as coordenadas originais.")
    
    def limpar_canvas(self):
        """Limpa o canvas atual"""
        if self.canvas_atual:
            self.canvas_atual.get_tk_widget().destroy()
            self.canvas_atual = None
            # Limpar apenas a figura do canvas, não as interativas
            try:
                # Fecha apenas figuras sem gerenciador de janela (embarcadas)
                for num in plt.get_fignums():
                    fig = plt.figure(num)
                    if not hasattr(fig.canvas, 'manager') or fig.canvas.manager is None:
                        plt.close(fig)
            except:
                pass
        # Forçar fechamento de todas as figuras matplotlib (evita loops/threads pendentes)
        try:
            plt.close('all')
        except Exception:
            pass

    def on_fechar(self):
        """Handler para fechamento da janela principal.

        Executa limpeza de canvases/figuras e encerra o mainloop corretamente.
        """
        try:
            # Limpar canvas embutidos
            self.limpar_canvas()

            # Fechar figura interativa se existir
            if hasattr(self, 'fig_interativa') and self.fig_interativa is not None:
                try:
                    if plt.fignum_exists(self.fig_interativa.number):
                        plt.close(self.fig_interativa)
                except Exception:
                    pass

            # Fechar todas as figuras restantes
            try:
                plt.close('all')
            except Exception:
                pass

            # Tentar destruir janelas filhas (se houver)
            try:
                for w in list(self.root.winfo_children()):
                    try:
                        w.destroy()
                    except Exception:
                        pass
            except Exception:
                pass

        finally:
            try:
                # Encerrar mainloop e destruir a janela principal
                try:
                    self.root.quit()
                except Exception:
                    pass
                try:
                    self.root.destroy()
                except Exception:
                    pass
            except Exception:
                pass
    
    def atualizar_resultados(self, texto):
        """Atualiza a área de resultados"""
        self.texto_resultados.delete(1.0, tk.END)
        self.texto_resultados.insert(1.0, texto)


def main():
    """Função principal"""
    root = tk.Tk()
    app = GraphApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

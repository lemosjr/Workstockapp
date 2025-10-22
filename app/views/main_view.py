import customtkinter as ctk
from tkinter import ttk, messagebox
# Importações das Views
from app.views.estoque_view import EstoqueView
from app.views.os_view import OSView
# Importações dos Controllers
from app.controllers import estoque_controller
from app.controllers import os_controller

"""
Camada View (Visão) Principal - A "casca" do aplicativo.
Agora com sistema de Abas.
"""

class MainView(ctk.CTk):
    
    def __init__(self):
        super().__init__()
        
        self.title("WorkStock - Gestão de Reformas")
        self.geometry("1200x700") # Janela maior
        
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        # Controladores das janelas de cadastro
        self.cadastro_estoque_window = None
        self.cadastro_os_window = None

        self.create_main_widgets()
        
        # Carrega os dados iniciais nas tabelas
        self.load_materials() 
        self.load_os()

    def create_main_widgets(self):
        # --- Frame Esquerdo (Navegação/Ações) ---
        # Este frame agora controla AMBAS as abas
        left_frame = ctk.CTkFrame(self, width=200)
        left_frame.pack(side="left", fill="y", padx=10, pady=10)

        ctk.CTkLabel(left_frame, text="Módulo OS", font=("Arial", 16)).pack(pady=10)
        
        nova_os_button = ctk.CTkButton(
            left_frame, 
            text="Criar Nova OS",
            command=self.abrir_cadastro_os # Nova função
        )
        nova_os_button.pack(pady=10)

        refresh_os_button = ctk.CTkButton(
            left_frame,
            text="Atualizar Lista de OS",
            command=self.load_os # Nova função
        )
        refresh_os_button.pack(pady=5)
        
        # Separador
        ctk.CTkFrame(left_frame, height=2, fg_color="gray").pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(left_frame, text="Módulo Estoque", font=("Arial", 16)).pack(pady=10)
        
        novo_material_button = ctk.CTkButton(
            left_frame, 
            text="Cadastrar Novo Material",
            command=self.abrir_cadastro_material
        )
        novo_material_button.pack(pady=10)

        refresh_material_button = ctk.CTkButton(
            left_frame,
            text="Atualizar Estoque",
            command=self.load_materials
        )
        refresh_material_button.pack(pady=5)

        # --- Frame Direito (Conteúdo com Abas) ---
        self.tab_view = ctk.CTkTabview(self)
        self.tab_view.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # Adiciona as abas
        self.tab_view.add("Ordens de Serviço")
        self.tab_view.add("Estoque")
        
        # Define a aba "OS" como padrão
        self.tab_view.set("Ordens de Serviço")

        # Cria as tabelas DENTRO das abas
        self.create_os_table(self.tab_view.tab("Ordens de Serviço"))
        self.create_materials_table(self.tab_view.tab("Estoque"))

    # --- Métodos do Módulo de Estoque (Quase Inalterados) ---

    def create_materials_table(self, parent_frame):
        # (O código de estilo do Treeview é omitido por brevidade,
        # mas cole o seu código anterior aqui)
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background="#2b2b2b", foreground="#dce4ee", fieldbackground="#343638", rowheight=25, borderwidth=0)
        style.map('Treeview', background=[('selected', '#3471CD')])
        style.configure("Treeview.Heading", background="#565B5E", foreground="#dce4ee", font=("Arial", 10, "bold"), relief="flat")
        style.map("Treeview.Heading", background=[('active', '#343638')])
        
        columns = ("id", "sku", "nome", "estoque_atual", "preco_custo", "unidade_medida")
        self.estoque_tree = ttk.Treeview(parent_frame, columns=columns, show="headings")
        
        self.estoque_tree.heading("id", text="ID")
        self.estoque_tree.heading("sku", text="SKU")
        self.estoque_tree.heading("nome", text="Nome")
        self.estoque_tree.heading("estoque_atual", text="Estoque")
        self.estoque_tree.heading("preco_custo", text="Preço (R$)")
        self.estoque_tree.heading("unidade_medida", text="Un.")
        
        self.estoque_tree.column("id", width=40, anchor="center")
        self.estoque_tree.column("sku", width=100)
        self.estoque_tree.column("nome", width=250)
        self.estoque_tree.column("estoque_atual", width=60, anchor="center")
        self.estoque_tree.column("preco_custo", width=80, anchor="e")
        self.estoque_tree.column("unidade_medida", width=50, anchor="center")
        
        self.estoque_tree.pack(fill="both", expand=True, padx=10, pady=10)

    def load_materials(self):
        for item in self.estoque_tree.get_children():
            self.estoque_tree.delete(item)
            
        sucesso, dados = estoque_controller.listar_materiais()
        
        if sucesso:
            for material in dados:
                valores = (
                    material['id'], material['sku'], material['nome'],
                    material['estoque_atual'], f"{material['preco_custo']:.2f}",
                    material['unidade_medida']
                )
                self.estoque_tree.insert("", "end", values=valores)
        else:
            messagebox.showerror("Erro", "Não foi possível carregar a lista de materiais.")

    def abrir_cadastro_material(self):
        if self.cadastro_estoque_window is None or not self.cadastro_estoque_window.winfo_exists():
            self.cadastro_estoque_window = EstoqueView(master=self)
            self.cadastro_estoque_window.bind("<Destroy>", self.on_estoque_cadastro_closed)
        else:
            self.cadastro_estoque_window.focus()

    def on_estoque_cadastro_closed(self, event):
        if event.widget == self.cadastro_estoque_window:
            self.load_materials()

    # --- Métodos do Módulo de OS (NOVOS) ---

    def create_os_table(self, parent_frame):
        """ Cria a tabela (Treeview) para exibir as OS. """
        
        # (Reutilizamos o estilo já configurado)
        
        columns = ("id", "status", "prioridade", "tipo_servico", "endereco", "data_abertura", "data_prevista")
        
        self.os_tree = ttk.Treeview(parent_frame, columns=columns, show="headings")
        
        self.os_tree.heading("id", text="OS #")
        self.os_tree.heading("status", text="Status")
        self.os_tree.heading("prioridade", text="Prioridade")
        self.os_tree.heading("tipo_servico", text="Serviço")
        self.os_tree.heading("endereco", text="Endereço")
        self.os_tree.heading("data_abertura", text="Data Abertura")
        self.os_tree.heading("data_prevista", text="Previsão Entrega")
        
        self.os_tree.column("id", width=50, anchor="center")
        self.os_tree.column("status", width=120)
        self.os_tree.column("prioridade", width=80)
        self.os_tree.column("tipo_servico", width=150)
        self.os_tree.column("endereco", width=250)
        self.os_tree.column("data_abertura", width=130, anchor="center")
        self.os_tree.column("data_prevista", width=130, anchor="center")
        
        self.os_tree.pack(fill="both", expand=True, padx=10, pady=10)

    def load_os(self):
        """ Busca os dados no OS_Controller e atualiza a tabela de OS. """
        print("View: Solicitando lista de OS ao Controller...")
        
        for item in self.os_tree.get_children():
            self.os_tree.delete(item)
            
        sucesso, dados = os_controller.listar_os()
        
        if sucesso:
            print(f"View: Recebeu {len(dados)} Ordens de Serviço.")
            for os in dados:
                # Formata as datas para exibição amigável
                data_abertura_fmt = os['data_abertura'].strftime('%d/%m/%Y %H:%M')
                data_prevista_fmt = os['data_conclusao_prevista'].strftime('%d/%m/%Y') if os['data_conclusao_prevista'] else "---"
                
                valores = (
                    os['id'],
                    os['status'].capitalize(),
                    os['prioridade'].capitalize(),
                    os['tipo_servico'],
                    os['endereco'],
                    data_abertura_fmt,
                    data_prevista_fmt
                )
                self.os_tree.insert("", "end", values=valores)
        else:
            messagebox.showerror("Erro", "Não foi possível carregar a lista de Ordens de Serviço.")

    def abrir_cadastro_os(self):
        """ Abre a janela de cadastro de OS. """
        if self.cadastro_os_window is None or not self.cadastro_os_window.winfo_exists():
            self.cadastro_os_window = OSView(master=self)
            self.cadastro_os_window.bind("<Destroy>", self.on_os_cadastro_closed)
        else:
            self.cadastro_os_window.focus()

    def on_os_cadastro_closed(self, event):
        """ Chamado quando a janela de cadastro de OS é fechada. """
        if event.widget == self.cadastro_os_window:
            print("View: Janela de OS fechada. Atualizando lista...")
            self.load_os()
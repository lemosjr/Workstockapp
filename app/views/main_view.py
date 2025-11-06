import customtkinter as ctk
from tkinter import ttk, messagebox
# Importações das Views
from app.views.estoque_view import EstoqueView
from app.views.os_view import OSView
from app.views.user_view import UserView
from app.views.gerenciar_materiais_view import GerenciarMateriaisView
# Importações dos Controllers
from app.controllers import estoque_controller
from app.controllers import os_controller

"""
Camada View (Visão) Principal - A "casca" do aplicativo.
Agora com sistema de Abas.
"""

class MainView(ctk.CTk):
    
    def __init__(self, user_data):
        super().__init__()
        
        # Armazena os dados do usuário logado
        self.user_data = user_data 
        
        self.title("WorkStock - Gestão de Reformas")
        self.geometry("1200x700")
        
        self.cadastro_estoque_window = None
        self.cadastro_os_window = None
        self.cadastro_user_window = None
        self.gerenciar_materiais_window = None

        self.create_main_widgets()
        
        self.load_materials() 
        self.load_os()

        self._apply_permissions()

    def create_main_widgets(self):
        # --- Frame Esquerdo (Navegação/Ações) ---
        left_frame = ctk.CTkFrame(self, width=200)
        left_frame.pack(side="left", fill="y", padx=10, pady=10)
        
        # --- INFO DO USUÁRIO ---
        ctk.CTkLabel(left_frame, text="Usuário Logado:", 
                     font=ctk.CTkFont(size=12, weight="bold")).pack(pady=(10, 0))
        
        user_nome = self.user_data.get('nome', 'Usuário') 
        ctk.CTkLabel(left_frame, text=user_nome,
                     font=ctk.CTkFont(size=14)).pack(pady=(0, 10))

        user_perfil = self.user_data.get('perfil', 'N/A').capitalize()
        ctk.CTkLabel(left_frame, text=f"Perfil: {user_perfil}",
                     font=ctk.CTkFont(size=11)).pack(pady=(0, 10))
        
        # --- SEÇÃO DE ADMINISTRAÇÃO ---
        ctk.CTkLabel(left_frame, text="Administração", 
                     font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(10, 0))

        self.user_button = ctk.CTkButton(
            left_frame, 
            text="Cadastrar Usuário",
            command=self.abrir_cadastro_usuario,
            state="disabled" # Começa desabilitado por padrão
        )
        self.user_button.pack(pady=10)
        
        ctk.CTkFrame(left_frame, height=2, fg_color="gray").pack(fill="x", padx=10, pady=10)
        # --- FIM DA SEÇÃO ---

        # --- MÓDULO OS ---
        ctk.CTkLabel(left_frame, text="Módulo OS", font=("Arial", 16)).pack(pady=10)
        
        self.nova_os_button = ctk.CTkButton(
            left_frame, 
            text="Criar Nova OS",
            command=lambda: self.abrir_cadastro_os(os_id=None)
        )
        self.nova_os_button.pack(pady=10)

        self.refresh_os_button = ctk.CTkButton(
            left_frame,
            text="Atualizar Lista de OS",
            command=self.load_os
        )
        self.refresh_os_button.pack(pady=5)
        
        self.delete_os_button = ctk.CTkButton(
            left_frame,
            text="Deletar OS",
            command=self._on_delete_os, # Nova função
            state="disabled", # Começa desabilitado
            fg_color="#DB3E3E", # Cor vermelha
            hover_color="#B73030"
        )
        self.delete_os_button.pack(pady=5)
        # --- FIM MÓDULO OS ---

        # --- BOTÃO GERENCIAR MATERIAIS ---
        self.gerenciar_materiais_button = ctk.CTkButton(
            left_frame,
            text="Gerenciar Materiais da OS",
            command=self._on_gerenciar_materiais, # Nova função
            state="disabled" # Começa desabilitado
        )
        self.gerenciar_materiais_button.pack(pady=5)
        
        ctk.CTkFrame(left_frame, height=2, fg_color="gray").pack(fill="x", padx=10, pady=10)

        # --- MÓDULO ESTOQUE ---
        ctk.CTkLabel(left_frame, text="Módulo Estoque", font=("Arial", 16)).pack(pady=10)
        
        self.novo_material_button = ctk.CTkButton(
            left_frame, 
            text="Cadastrar Novo Material",
            command=self.abrir_cadastro_material
        )
        self.novo_material_button.pack(pady=10)

        self.refresh_material_button = ctk.CTkButton(
            left_frame,
            text="Atualizar Estoque",
            command=self.load_materials
        )
        self.refresh_material_button.pack(pady=5)

        self.delete_material_button = ctk.CTkButton(
            left_frame,
            text="Deletar Material",
            command=self._on_delete_material,
            state="disabled", # Começa desabilitado
            fg_color="#DB3E3E", # Cor vermelha para "perigo"
            hover_color="#B73030"
        )
        self.delete_material_button.pack(pady=5)
        # --- FIM MÓDULO ESTOQUE ---


        # --- Frame Direito (Conteúdo com Abas) ---
        self.tab_view = ctk.CTkTabview(self)
        self.tab_view.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        self.tab_view.add("Ordens de Serviço")
        self.tab_view.add("Estoque")
        self.tab_view.set("Ordens de Serviço") # Define a aba "OS" como padrão

        self.create_os_table(self.tab_view.tab("Ordens de Serviço"))
        self.create_materials_table(self.tab_view.tab("Estoque"))

    # --- Métodos de Gestão (Usuário) ---

    def abrir_cadastro_usuario(self):
        """ Abre a janela de cadastro de Usuário. """
        if self.cadastro_user_window is None or not self.cadastro_user_window.winfo_exists():
            self.cadastro_user_window = UserView(master=self)
        else:
            self.cadastro_user_window.focus()

    # --- Métodos do Módulo de Estoque ---

    def _on_delete_material(self):
        """ Chamado pelo botão "Deletar Material". """
        try:
            selected_item = self.estoque_tree.focus()
            if not selected_item:
                messagebox.showwarning("Aviso", "Por favor, selecione um material na tabela para deletar.")
                return

            item_values = self.estoque_tree.item(selected_item, "values")
            material_id = int(item_values[0])
            material_name = item_values[2] 

            confirm = messagebox.askyesno(
                "Confirmar Exclusão",
                f"Tem certeza que deseja deletar o material:\n\n"
                f"ID: {material_id}\n"
                f"Nome: {material_name}\n\n"
                f"Esta ação não pode ser desfeita."
            )
            
            if not confirm:
                return 

            print(f"View (Main): Solicitando ao controller para deletar material ID {material_id}")
            sucesso, msg = estoque_controller.deletar_material(material_id)
            
            if sucesso:
                messagebox.showinfo("Sucesso", msg)
                self.load_materials() 
            else:
                messagebox.showerror("Erro ao Deletar", msg)
        
        except (IndexError, TypeError, ValueError) as e:
            print(f"View (Main) Erro: Não foi possível obter o ID do material. {e}")
            messagebox.showwarning("Aviso", "Não foi possível identificar o material selecionado. Tente novamente.")

    def create_materials_table(self, parent_frame):
        """ Cria a tabela (Treeview) para exibir os materiais. """
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
        
        # (Futuramente podemos adicionar o duplo-clique para editar material)
        # self.estoque_tree.bind("<Double-1>", self._on_estoque_double_click)

    def load_materials(self):
        """ Carrega os materiais do controller para a tabela. """
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
        """ Abre a janela de cadastro de material. """
        # (Aqui ainda não implementamos a edição, apenas criação)
        if self.cadastro_estoque_window is None or not self.cadastro_estoque_window.winfo_exists():
            self.cadastro_estoque_window = EstoqueView(master=self)
            self.cadastro_estoque_window.bind("<Destroy>", self.on_estoque_cadastro_closed)
        else:
            self.cadastro_estoque_window.focus()

    def on_estoque_cadastro_closed(self, event):
        """ Chamado quando a janela de cadastro de estoque fecha. """
        if event.widget == self.cadastro_estoque_window:
            self.load_materials() # Atualiza a lista

    # --- Métodos do Módulo de OS ---

    def _on_delete_os(self):
        """ Chamado pelo botão "Deletar OS". """
        try:
            selected_item = self.os_tree.focus()
            if not selected_item:
                messagebox.showwarning("Aviso", "Por favor, selecione uma Ordem de Serviço na tabela para deletar.")
                return

            item_values = self.os_tree.item(selected_item, "values")
            os_id = int(item_values[0])
            os_tipo = item_values[3] 
            os_endereco = item_values[4]

            confirm = messagebox.askyesno(
                "Confirmar Exclusão",
                f"Tem certeza que deseja deletar a Ordem de Serviço:\n\n"
                f"OS #: {os_id}\n"
                f"Serviço: {os_tipo}\n"
                f"Endereço: {os_endereco}\n\n"
                f"Esta ação não pode ser desfeita."
            )
            
            if not confirm:
                return 

            print(f"View (Main): Solicitando ao controller para deletar OS ID {os_id}")
            sucesso, msg = os_controller.deletar_os(os_id)
            
            if sucesso:
                messagebox.showinfo("Sucesso", msg)
                self.load_os() # Atualiza a tabela de OS
            else:
                messagebox.showerror("Erro ao Deletar", msg)
        
        except (IndexError, TypeError, ValueError) as e:
            print(f"View (Main) Erro: Não foi possível obter o ID da OS. {e}")
            messagebox.showwarning("Aviso", "Não foi possível identificar a OS selecionada. Tente novamente.")

    def create_os_table(self, parent_frame):
        """ Cria a tabela (Treeview) para exibir as OS. """
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

        # Liga o duplo-clique para ATUALIZAR
        self.os_tree.bind("<Double-1>", self._on_os_double_click)

    def load_os(self):
        """ Carrega as OSs do controller para a tabela. """
        print("View: Solicitando lista de OS ao Controller...")
        
        for item in self.os_tree.get_children():
            self.os_tree.delete(item)
            
        sucesso, dados = os_controller.listar_os()
        
        if sucesso:
            print(f"View: Recebeu {len(dados)} Ordens de Serviço.")
            for os in dados:
                data_abertura_fmt = os['data_abertura'].strftime('%d/%m/%Y %H:%M')
                data_prevista_fmt = os['data_conclusao_prevista'].strftime('%d/%m/%Y') if os['data_conclusao_prevista'] else "---"
                
                valores = (
                    os['id'], os['status'].capitalize(), os['prioridade'].capitalize(),
                    os['tipo_servico'], os['endereco'],
                    data_abertura_fmt, data_prevista_fmt
                )
                self.os_tree.insert("", "end", values=valores)
        else:
            messagebox.showerror("Erro", "Não foi possível carregar a lista de Ordens de Serviço.")

    def abrir_cadastro_os(self, os_id=None):
        """ Abre a janela de cadastro/edição de OS. """
        if self.cadastro_os_window is None or not self.cadastro_os_window.winfo_exists():
            self.cadastro_os_window = OSView(master=self, os_id=os_id) 
            self.cadastro_os_window.bind("<Destroy>", self.on_os_cadastro_closed)
        else:
            self.cadastro_os_window.focus()
            
    def _on_os_double_click(self, event):
        """ Chamado pelo duplo-clique na tabela de OS para editar. """
        try:
            selected_item = self.os_tree.focus() 
            if not selected_item:
                return 

            item_values = self.os_tree.item(selected_item, "values")
            os_id = int(item_values[0])
            
            print(f"View (Main): Duplo-clique detectado. Abrindo edição para OS #{os_id}")
            self.abrir_cadastro_os(os_id=os_id)
            
        except (IndexError, TypeError, ValueError) as e:
            print(f"View (Main) Erro: Não foi possível obter o ID da OS. {e}")
            messagebox.showwarning("Aviso", "Não foi possível selecionar a OS. Tente novamente.")

    def on_os_cadastro_closed(self, event):
        """ Chamado quando a janela de cadastro de OS fecha. """
        if event.widget == self.cadastro_os_window:
            print("View: Janela de OS fechada. Atualizando lista...")
            self.load_os()
            
    # --- Método de Permissões ---

    def _apply_permissions(self):
        """ Ajusta a UI com base no perfil do usuário logado. """
        
        perfil = self.user_data.get('perfil')
        print(f"View (Main): Aplicando permissões para o perfil: '{perfil}'")
        
        if perfil == 'empresa':
            # Habilita todas as funções de admin
            self.user_button.configure(state="normal")
            self.delete_material_button.configure(state="normal")
            self.delete_os_button.configure(state="normal")
            self.gerenciar_materiais_button.configure(state="normal")

            print("View (Main): Acesso de 'Empresa' concedido.")
            return

        # --- Regras para outros perfis (restringir) ---
        
        # (Todos os botões de admin já começam 'disabled')
        
        if perfil == 'proprietario':
            print("View (Main): Acesso de 'Proprietário' concedido.")
            self.nova_os_button.configure(state="disabled")
            self.novo_material_button.configure(state="disabled")
            self.refresh_material_button.configure(state="disabled")
            
        elif perfil == 'cliente':
            print("View (Main): Acesso de 'Cliente' concedido.")
            self.nova_os_button.configure(state="disabled")
            self.novo_material_button.configure(state="disabled")
            self.refresh_material_button.configure(state="disabled")
            
        else: # Perfil desconhecido (segurança)
            print(f"View (Main): Perfil desconhecido '{perfil}'. Bloqueando tudo.")
            self.nova_os_button.configure(state="disabled")
            self.refresh_os_button.configure(state="disabled")
            self.novo_material_button.configure(state="disabled")
            self.refresh_material_button.configure(state="disabled")
            
        # Oculta a aba de Estoque para não-empresas
        try:
            self.tab_view.delete("Estoque")
        except Exception:
            pass # Ignora se a aba já foi deletada

    # --- MÉTODO NOVO ---
    def _on_gerenciar_materiais(self):
        """
        Chamado pelo botão "Gerenciar Materiais da OS".
        Abre a janela de gerenciamento para a OS selecionada.
        """
        try:
            # 1. Pega a OS selecionada na tabela
            selected_item = self.os_tree.focus()
            if not selected_item:
                messagebox.showwarning("Aviso", "Por favor, selecione uma Ordem de Serviço na tabela primeiro.")
                return

            # 2. Pega o ID da OS
            item_values = self.os_tree.item(selected_item, "values")
            os_id = int(item_values[0])
            
            print(f"View (Main): Abrindo gerenciador de materiais para OS #{os_id}")

            # 3. Abre a nova janela
            if self.gerenciar_materiais_window is None or not self.gerenciar_materiais_window.winfo_exists():
                self.gerenciar_materiais_window = GerenciarMateriaisView(master=self, os_id=os_id)
                # BIND: Quando a janela fechar, atualize as listas!
                self.gerenciar_materiais_window.bind("<Destroy>", self.on_materiais_closed)
            else:
                self.gerenciar_materiais_window.focus()
        
        except (IndexError, TypeError, ValueError) as e:
            print(f"View (Main) Erro: Não foi possível obter o ID da OS. {e}")
            messagebox.showwarning("Aviso", "Não foi possível identificar a OS selecionada. Tente novamente.")

    # --- MÉTODO NOVO ---
    def on_materiais_closed(self, event):
        """
        Chamado quando a janela GerenciarMateriaisView é fechada.
        Atualiza as listas de OS e Estoque.
        """
        # Verifica se o evento veio da janela correta
        if event.widget == self.gerenciar_materiais_window:
            print("View (Main): Janela de materiais fechada. Atualizando listas...")
            # Atualiza AMBAS as listas, pois o estoque mudou
            self.load_materials()
            self.load_os() # (Pode ter atualizações futuras, como custo total)
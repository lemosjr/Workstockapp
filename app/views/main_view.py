import customtkinter as ctk
from tkinter import ttk, messagebox
# Importações das Views
from app.views.estoque_view import EstoqueView
from app.views.os_view import OSView
from app.views.user_view import UserView
from app.views.gerenciar_materiais_view import GerenciarMateriaisView
from app.views.solicitacao_view import SolicitacaoView
from app.views.chat_view import ChatView
from app.controllers import dashboard_controller
# Importações dos Controllers
from app.controllers import estoque_controller
from app.controllers import os_controller

# --- PALETA DE CORES ---
COLOR_PRIMARY = "#264653"   # Teal Escuro (Sidebar, Headers)
COLOR_SECONDARY = "#2A5159" # Teal Médio (Hover Sidebar, Separadores)
COLOR_BG_LIGHT = "#F2F2F2"  # Off-white
COLOR_ACCENT = "#F2B263"    # Laranja (Ações Principais)
COLOR_ACCENT_HOVER = "#D9A059"
COLOR_DANGER = "#BF4124"    # Vermelho (Perigo)
COLOR_DANGER_HOVER = "#A6391F"
COLOR_TEXT_DARK = "#264653" # Texto sobre fundo laranja

class MainView(ctk.CTk):
    
    def __init__(self, user_data):
        super().__init__()
        
        self.user_data = user_data 
        self.title("WorkStock - Gestão de Reformas")
        self.geometry("1200x700")
        
        self.cadastro_estoque_window = None
        self.cadastro_os_window = None
        self.cadastro_user_window = None
        self.gerenciar_materiais_window = None
        self.solicitacao_window = None
        self.chat_window = None

        self.create_main_widgets()
        self.load_materials() 
        self.load_os()
        self._apply_permissions()

    def create_main_widgets(self):
        # --- Sidebar (Esquerda) com a cor TEAL ESCURO ---
        self.left_frame = ctk.CTkFrame(self, width=240, corner_radius=0, fg_color=COLOR_PRIMARY)
        self.left_frame.pack(side="left", fill="y")
        
        # --- INFO DO USUÁRIO ---
        self.logo_label = ctk.CTkLabel(
            self.left_frame, text="WorkStock", 
            font=("Roboto Medium", 22), text_color=COLOR_ACCENT
        )
        self.logo_label.pack(pady=(30, 10))

        user_nome = self.user_data.get('nome', 'Usuário')
        user_perfil = self.user_data.get('perfil', 'N/A').capitalize()
        
        self.user_info_label = ctk.CTkLabel(
            self.left_frame, 
            text=f"Olá, {user_nome}\n({user_perfil})",
            font=("Roboto", 12), text_color="#DCE4EE"
        )
        self.user_info_label.pack(pady=(0, 20))
        
        # --- SEÇÃO DE ADMINISTRAÇÃO ---
        self.admin_label = ctk.CTkLabel(self.left_frame, text="ADMINISTRAÇÃO", 
                     font=("Roboto", 12, "bold"), text_color="#AABEC9", anchor="w")
        self.admin_label.pack(pady=(10, 5), padx=20, fill="x")

        self.user_button = self._create_sidebar_button("Cadastrar Usuário", self.abrir_cadastro_usuario)
        self.user_button.pack(pady=5, padx=20, fill="x")
        
        # [CORREÇÃO] Criando o separador de admin
        self.admin_separator = ctk.CTkFrame(self.left_frame, height=2, fg_color=COLOR_SECONDARY)
        self.admin_separator.pack(fill="x", padx=20, pady=10)
        
        # --- MÓDULO OS ---
        self.os_label = ctk.CTkLabel(self.left_frame, text="ORDENS DE SERVIÇO", 
                     font=("Roboto", 12, "bold"), text_color="#AABEC9", anchor="w")
        self.os_label.pack(pady=(10, 5), padx=20, fill="x")
        
        self.nova_os_button = ctk.CTkButton(
            self.left_frame, text="+ Nova OS",
            command=lambda: self.abrir_cadastro_os(os_id=None),
            fg_color=COLOR_ACCENT, hover_color=COLOR_ACCENT_HOVER, text_color=COLOR_TEXT_DARK,
            font=("Roboto Medium", 13)
        )
        self.nova_os_button.pack(pady=5, padx=20, fill="x")

        self.refresh_os_button = self._create_sidebar_button("Atualizar Lista", self.load_os)
        self.refresh_os_button.pack(pady=5, padx=20, fill="x")
        
        self.chat_button = self._create_sidebar_button("Ver Chat da OS", self._on_ver_chat)
        self.chat_button.pack(pady=5, padx=20, fill="x")

        self.delete_os_button = ctk.CTkButton(
            self.left_frame, text="Deletar OS", command=self._on_delete_os,
            state="disabled", fg_color="transparent", border_width=1, 
            border_color=COLOR_DANGER, text_color=COLOR_DANGER, hover_color=COLOR_PRIMARY
        )
        self.delete_os_button.pack(pady=5, padx=20, fill="x")

        self.gerenciar_materiais_button = self._create_sidebar_button("Gerenciar Materiais", self._on_gerenciar_materiais)
        self.gerenciar_materiais_button.pack(pady=5, padx=20, fill="x")
        
        # --- FLUXO DE ORÇAMENTO ---
        self.orcamento_label = ctk.CTkLabel(self.left_frame, text="ORÇAMENTOS", 
                     font=("Roboto", 12, "bold"), text_color="#AABEC9", anchor="w")
        self.orcamento_label.pack(pady=(20, 5), padx=20, fill="x")
        
        self.enviar_orcamento_button = self._create_sidebar_button("Enviar p/ Aprovação", self._on_enviar_orcamento)
        self.enviar_orcamento_button.pack(pady=5, padx=20, fill="x")

        self.aprovar_orcamento_button = ctk.CTkButton(
            self.left_frame, text="Aprovar Orçamento",
            command=self._on_aprovar_orcamento, state="disabled",
            fg_color=COLOR_ACCENT, hover_color=COLOR_ACCENT_HOVER, text_color=COLOR_TEXT_DARK
        )
        self.aprovar_orcamento_button.pack(pady=5, padx=20, fill="x")
        
        self.rejeitar_orcamento_button = ctk.CTkButton(
            self.left_frame, text="Rejeitar Orçamento",
            command=self._on_rejeitar_orcamento, state="disabled",
            fg_color=COLOR_DANGER, hover_color=COLOR_DANGER_HOVER, text_color="white"
        )
        self.rejeitar_orcamento_button.pack(pady=5, padx=20, fill="x")
        
        # [CORREÇÃO] Criando o separador de orçamento
        self.orcamento_separator = ctk.CTkFrame(self.left_frame, height=2, fg_color=COLOR_SECONDARY)
        self.orcamento_separator.pack(fill="x", padx=20, pady=10)
        
        # --- MÓDULO ESTOQUE ---
        self.estoque_label = ctk.CTkLabel(self.left_frame, text="ESTOQUE", 
                     font=("Roboto", 12, "bold"), text_color="#AABEC9", anchor="w")
        self.estoque_label.pack(pady=(10, 5), padx=20, fill="x")
        
        self.novo_material_button = ctk.CTkButton(
            self.left_frame, text="+ Novo Material",
            command=self.abrir_cadastro_material,
            fg_color=COLOR_ACCENT, hover_color=COLOR_ACCENT_HOVER, text_color=COLOR_TEXT_DARK
        )
        self.novo_material_button.pack(pady=5, padx=20, fill="x")

        self.refresh_material_button = self._create_sidebar_button("Atualizar Estoque", self.load_materials)
        self.refresh_material_button.pack(pady=5, padx=20, fill="x")

        self.delete_material_button = ctk.CTkButton(
            self.left_frame, text="Deletar Material",
            command=self._on_delete_material, state="disabled",
            fg_color="transparent", border_width=1, 
            border_color=COLOR_DANGER, text_color=COLOR_DANGER, hover_color=COLOR_PRIMARY
        )
        self.delete_material_button.pack(pady=5, padx=20, fill="x")
        
        # --- MÓDULO CLIENTE ---
        self.cliente_label = ctk.CTkLabel(self.left_frame, text="MINHA CONTA", 
                     font=("Roboto", 12, "bold"), text_color="#AABEC9", anchor="w")

        self.nova_solicitacao_button = ctk.CTkButton(
            self.left_frame, text="+ Fazer Solicitação",
            command=self.abrir_nova_solicitacao,
            fg_color=COLOR_ACCENT, hover_color=COLOR_ACCENT_HOVER, text_color=COLOR_TEXT_DARK
        )

        # --- Frame Direito (Conteúdo com Abas) ---
        self.tab_view = ctk.CTkTabview(self, fg_color="transparent")
        self.tab_view.pack(side="right", fill="both", expand=True, padx=20, pady=20)

        self.tab_view.add("Ordens de Serviço")
        self.tab_view.add("Estoque")
        self.tab_view.set("Ordens de Serviço") 

        self.create_os_table(self.tab_view.tab("Ordens de Serviço"))
        self.create_materials_table(self.tab_view.tab("Estoque"))

    def _create_sidebar_button(self, text, command):
        """ Helper para criar botões padrão da sidebar """
        return ctk.CTkButton(
            self.left_frame, 
            text=text, 
            command=command,
            fg_color="transparent", 
            border_width=1,
            border_color="#3E5F6B",
            text_color=COLOR_BG_LIGHT,
            hover_color=COLOR_SECONDARY
        )

    # --- Métodos de Gestão (Usuário/Admin) ---

    def abrir_cadastro_usuario(self):
        if self.cadastro_user_window is None or not self.cadastro_user_window.winfo_exists():
            self.cadastro_user_window = UserView(master=self)
        else:
            self.cadastro_user_window.focus()
            
    # --- MÓDULO CLIENTE ---
    
    def abrir_nova_solicitacao(self):
        if self.solicitacao_window is None or not self.solicitacao_window.winfo_exists():
            cliente_id = self.user_data['id']
            self.solicitacao_window = SolicitacaoView(master=self, user_id=cliente_id)
            self.solicitacao_window.bind("<Destroy>", self.on_solicitacao_closed)
        else:
            self.solicitacao_window.focus()

    def on_solicitacao_closed(self, event):
        if event.widget == self.solicitacao_window:
            self.load_os()

    # --- Métodos do Módulo de Estoque ---

    def _on_delete_material(self):
        try:
            selected_item = self.estoque_tree.focus()
            if not selected_item:
                messagebox.showwarning("Aviso", "Por favor, selecione um material na tabela para deletar.")
                return
            item_values = self.estoque_tree.item(selected_item, "values")
            material_id = int(item_values[0])
            material_name = item_values[2] 
            confirm = messagebox.askyesno("Confirmar Exclusão",f"Tem certeza que deseja deletar o material:\n\nID: {material_id}\nNome: {material_name}\n\nEsta ação não pode ser desfeita.")
            if not confirm: return 
            sucesso, msg = estoque_controller.deletar_material(material_id)
            if sucesso:
                messagebox.showinfo("Sucesso", msg)
                self.load_materials() 
            else:
                messagebox.showerror("Erro ao Deletar", msg)
        except (IndexError, TypeError, ValueError) as e:
            print(f"View (Main) Erro: Não foi possível obter o ID do material. {e}")
            messagebox.showwarning("Aviso", "Não foi possível identificar o material selecionado.")

    def create_materials_table(self, parent_frame):
        # Estilo da Tabela (Aplicando a Paleta)
        style = ttk.Style()
        style.theme_use("default")
        
        style.configure("Treeview", 
                        background="#2b2b2b", 
                        foreground=COLOR_BG_LIGHT, 
                        fieldbackground="#2b2b2b", 
                        rowheight=30, 
                        borderwidth=0)
        
        style.map('Treeview', background=[('selected', COLOR_ACCENT)], foreground=[('selected', COLOR_TEXT_DARK)])
        
        style.configure("Treeview.Heading", 
                        background=COLOR_PRIMARY, 
                        foreground=COLOR_BG_LIGHT, 
                        font=("Roboto", 10, "bold"), 
                        relief="flat")
        
        style.map("Treeview.Heading", background=[('active', COLOR_SECONDARY)])
        
        columns = ("id", "sku", "nome", "estoque_atual", "preco_custo", "unidade_medida")
        self.estoque_tree = ttk.Treeview(parent_frame, columns=columns, show="headings")
        
        self.estoque_tree.heading("id", text="ID"); self.estoque_tree.heading("sku", text="SKU"); self.estoque_tree.heading("nome", text="Nome"); self.estoque_tree.heading("estoque_atual", text="Estoque"); self.estoque_tree.heading("preco_custo", text="Preço (R$)"); self.estoque_tree.heading("unidade_medida", text="Un.")
        self.estoque_tree.column("id", width=40, anchor="center"); self.estoque_tree.column("sku", width=100); self.estoque_tree.column("nome", width=250); self.estoque_tree.column("estoque_atual", width=60, anchor="center"); self.estoque_tree.column("preco_custo", width=80, anchor="e"); self.estoque_tree.column("unidade_medida", width=50, anchor="center")
        self.estoque_tree.pack(fill="both", expand=True, padx=0, pady=0)

    def create_dashboard_tab(self, parent_frame):
        """ Cria o conteúdo da aba Dashboard (Cards de Estatísticas). """
        
        # Busca os dados
        sucesso, data = dashboard_controller.get_dashboard_data()
        if not sucesso: return

        # Configuração de Grid
        parent_frame.columnconfigure((0, 1), weight=1)
        
        # --- CARD 1: OS EM ANDAMENTO ---
        card1 = ctk.CTkFrame(parent_frame, fg_color=COLOR_PRIMARY, corner_radius=15)
        card1.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        ctk.CTkLabel(card1, text="Em Andamento", font=("Roboto", 14), text_color="#AABEC9").pack(pady=(15, 0))
        ctk.CTkLabel(card1, text=str(data['os_andamento']), font=("Roboto", 36, "bold"), text_color="white").pack(pady=(0, 15))

        # --- CARD 2: PENDENTES DE APROVAÇÃO ---
        card2 = ctk.CTkFrame(parent_frame, fg_color=COLOR_ACCENT, corner_radius=15)
        card2.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        ctk.CTkLabel(card2, text="Aguardando Aprovação", font=("Roboto", 14), text_color=COLOR_TEXT_DARK).pack(pady=(15, 0))
        ctk.CTkLabel(card2, text=str(data['os_pendentes']), font=("Roboto", 36, "bold"), text_color=COLOR_TEXT_DARK).pack(pady=(0, 15))

        # --- CARD 3: ALERTAS DE ESTOQUE ---
        # (Fica vermelho se houver alertas)
        color_estoque = COLOR_DANGER if data['alertas_estoque'] > 0 else COLOR_PRIMARY
        
        card3 = ctk.CTkFrame(parent_frame, fg_color=color_estoque, corner_radius=15)
        card3.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        
        ctk.CTkLabel(card3, text="Estoque Baixo (Itens)", font=("Roboto", 14), text_color="white").pack(pady=(15, 0))
        ctk.CTkLabel(card3, text=str(data['alertas_estoque']), font=("Roboto", 36, "bold"), text_color="white").pack(pady=(0, 15))

        # --- CARD 4: VALOR EM PROJETOS ---
        card4 = ctk.CTkFrame(parent_frame, fg_color=COLOR_PRIMARY, corner_radius=15)
        card4.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        
        val_fmt = f"R$ {data['faturamento']:.2f}"
        ctk.CTkLabel(card4, text="Valor em Obras (Ativas/Concluídas)", font=("Roboto", 14), text_color="#AABEC9").pack(pady=(15, 0))
        ctk.CTkLabel(card4, text=val_fmt, font=("Roboto", 28, "bold"), text_color="#4CAF50").pack(pady=(0, 15))
        
        # Botão de Atualizar Dashboard
        ctk.CTkButton(parent_frame, text="Atualizar Dados", 
                      fg_color="transparent", border_width=1, border_color=COLOR_PRIMARY, text_color=COLOR_PRIMARY,
                      command=lambda: self.create_dashboard_tab(parent_frame)).grid(row=2, column=0, columnspan=2, pady=20)

    def load_materials(self):
        for item in self.estoque_tree.get_children(): self.estoque_tree.delete(item)
        sucesso, dados = estoque_controller.listar_materiais()
        if sucesso:
            for material in dados:
                valores = (material['id'], material['sku'], material['nome'], material['estoque_atual'], f"{material['preco_custo']:.2f}", material['unidade_medida'])
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

    # --- Métodos do Módulo de OS ---

    def _get_selected_os_id(self):
        selected_item = self.os_tree.focus()
        if not selected_item:
            messagebox.showwarning("Aviso", "Por favor, selecione uma Ordem de Serviço na tabela primeiro.")
            return None
        try:
            item_values = self.os_tree.item(selected_item, "values")
            os_id = int(item_values[0])
            return os_id
        except (IndexError, TypeError, ValueError):
            messagebox.showwarning("Aviso", "Não foi possível identificar a OS selecionada.")
            return None

    def _on_delete_os(self):
        os_id = self._get_selected_os_id()
        if not os_id: return
        item_values = self.os_tree.item(self.os_tree.focus(), "values")
        os_tipo = item_values[3]; os_endereco = item_values[4]
        confirm = messagebox.askyesno("Confirmar Exclusão",f"Tem certeza que deseja deletar a Ordem de Serviço:\n\nOS #: {os_id}\nServiço: {os_tipo}\nEndereço: {os_endereco}\n\nEsta ação não pode ser desfeita.")
        if not confirm: return 
        sucesso, msg = os_controller.deletar_os(os_id)
        if sucesso:
            messagebox.showinfo("Sucesso", msg)
            self.load_os()
        else:
            messagebox.showerror("Erro ao Deletar", msg)
    
    def _on_gerenciar_materiais(self):
        os_id = self._get_selected_os_id()
        if not os_id: return
        if self.gerenciar_materiais_window is None or not self.gerenciar_materiais_window.winfo_exists():
            self.gerenciar_materiais_window = GerenciarMateriaisView(master=self, os_id=os_id)
            self.gerenciar_materiais_window.bind("<Destroy>", self.on_materiais_closed)
        else:
            self.gerenciar_materiais_window.focus()

    def on_materiais_closed(self, event):
        if event.widget == self.gerenciar_materiais_window:
            self.load_materials()
            self.load_os()
    
    def _on_enviar_orcamento(self):
        os_id = self._get_selected_os_id()
        if not os_id: return
        confirm = messagebox.askyesno("Confirmar Envio",f"Deseja enviar o orçamento da OS #{os_id} para aprovação?\n\nIsso irá mudar o status para 'Aguardando Aprovação'.")
        if not confirm: return
        sucesso, msg = os_controller.enviar_orcamento_para_aprovacao(os_id)
        if sucesso:
            messagebox.showinfo("Sucesso", msg)
            self.load_os()
        else:
            messagebox.showerror("Erro ao Enviar", msg)

    def _on_aprovar_orcamento(self):
        os_id = self._get_selected_os_id()
        if not os_id: return
        confirm = messagebox.askyesno("Confirmar Aprovação",f"Deseja APROVAR o orçamento da OS #{os_id}?\n\nO status mudará para 'Em Andamento'.")
        if not confirm: return
        sucesso, msg = os_controller.aprovar_orcamento_os(os_id)
        if sucesso:
            messagebox.showinfo("Sucesso", msg)
            self.load_os()
        else:
            messagebox.showerror("Erro ao Aprovar", msg)

    def _on_rejeitar_orcamento(self):
        os_id = self._get_selected_os_id()
        if not os_id: return
        confirm = messagebox.askyesno("Confirmar Rejeição",f"Deseja REJEITAR o orçamento da OS #{os_id}?\n\nO status voltará para 'Aberta'.")
        if not confirm: return
        sucesso, msg = os_controller.rejeitar_orcamento_os(os_id)
        if sucesso:
            messagebox.showinfo("Sucesso", msg)
            self.load_os()
        else:
            messagebox.showerror("Erro ao Rejeitar", msg)
    
    def _on_ver_chat(self):
        os_id = self._get_selected_os_id()
        if not os_id: return
        current_user_id = self.user_data['id']
        if self.chat_window is None or not self.chat_window.winfo_exists():
            self.chat_window = ChatView(master=self, os_id=os_id, current_user_id=current_user_id)
        else:
            self.chat_window.focus()

    def create_os_table(self, parent_frame):
        # Estilo da Tabela (Mesmo do Estoque)
        columns = ("id", "status", "prioridade", "tipo_servico", "endereco", "data_abertura", "data_prevista")
        self.os_tree = ttk.Treeview(parent_frame, columns=columns, show="headings")
        self.os_tree.heading("id", text="OS #"); self.os_tree.heading("status", text="Status"); self.os_tree.heading("prioridade", text="Prioridade"); self.os_tree.heading("tipo_servico", text="Serviço"); self.os_tree.heading("endereco", text="Endereço"); self.os_tree.heading("data_abertura", text="Data Abertura"); self.os_tree.heading("data_prevista", text="Previsão Entrega")
        self.os_tree.column("id", width=50, anchor="center"); self.os_tree.column("status", width=120); self.os_tree.column("prioridade", width=80); self.os_tree.column("tipo_servico", width=150); self.os_tree.column("endereco", width=250); self.os_tree.column("data_abertura", width=130, anchor="center"); self.os_tree.column("data_prevista", width=130, anchor="center")
        self.os_tree.pack(fill="both", expand=True, padx=0, pady=0)
        self.os_tree.bind("<Double-1>", self._on_os_double_click)

    def load_os(self):
        for item in self.os_tree.get_children(): self.os_tree.delete(item)
        
        user_id = self.user_data.get('id')
        user_perfil = self.user_data.get('perfil')
        sucesso, dados = os_controller.listar_os(user_id, user_perfil)
        
        if sucesso:
            for os in dados:
                data_abertura_fmt = os['data_abertura'].strftime('%d/%m/%Y %H:%M')
                data_prevista_fmt = os['data_conclusao_prevista'].strftime('%d/%m/%Y') if os['data_conclusao_prevista'] else "---"
                valores = (os['id'], os['status'].capitalize(), os['prioridade'].capitalize(), os['tipo_servico'], os['endereco'], data_abertura_fmt, data_prevista_fmt)
                self.os_tree.insert("", "end", values=valores)
        else:
            messagebox.showerror("Erro", "Não foi possível carregar a lista de Ordens de Serviço.")

    def abrir_cadastro_os(self, os_id=None):
        if self.cadastro_os_window is None or not self.cadastro_os_window.winfo_exists():
            self.cadastro_os_window = OSView(master=self, os_id=os_id) 
            self.cadastro_os_window.bind("<Destroy>", self.on_os_cadastro_closed)
        else:
            self.cadastro_os_window.focus()
            
    def _on_os_double_click(self, event):
        os_id = self._get_selected_os_id()
        if not os_id: return
        self.abrir_cadastro_os(os_id=os_id)

    def on_os_cadastro_closed(self, event):
        if event.widget == self.cadastro_os_window:
            self.load_os()
            
    # --- Método de Permissões (ATUALIZADO) ---

    def _apply_permissions(self):
        """ 
        Ajusta a UI com base no perfil do usuário logado.
        Esta é a implementação de "Segurança por Padrão".
        """
        
        perfil = self.user_data.get('perfil')
        print(f"View (Main): Aplicando permissões para o perfil: '{perfil}'")

        # --- 1. ESCONDE TUDO PRIMEIRO (Reset) ---
        # Esconde widgets da sidebar
        self.admin_label.pack_forget()
        self.user_button.pack_forget()
        self.admin_separator.pack_forget()
        
        self.os_label.pack_forget()
        self.nova_os_button.pack_forget()
        self.refresh_os_button.pack_forget()
        self.chat_button.pack_forget()
        self.delete_os_button.pack_forget()
        self.gerenciar_materiais_button.pack_forget()
        
        self.orcamento_label.pack_forget()
        self.enviar_orcamento_button.pack_forget()
        self.aprovar_orcamento_button.pack_forget()
        self.rejeitar_orcamento_button.pack_forget()
        self.orcamento_separator.pack_forget()
        
        self.estoque_label.pack_forget()
        self.novo_material_button.pack_forget()
        self.refresh_material_button.pack_forget()
        self.delete_material_button.pack_forget()
        
        self.cliente_label.pack_forget()
        self.nova_solicitacao_button.pack_forget()
        
        # Remove TODAS as abas para recriar na ordem certa depois
        for aba in ["Dashboard", "Estoque", "Ordens de Serviço"]:
            try: 
                self.tab_view.delete(aba)
            except Exception: 
                pass 


        # --- 2. HABILITA SEÇÕES COM BASE NO PERFIL ---
        
        if perfil == 'empresa':
            print("View (Main): Acesso de 'Empresa' concedido.")
            
            # --- Sidebar ---
            self.admin_label.pack(pady=(10, 5), padx=20, fill="x")
            self.user_button.pack(pady=5, padx=20, fill="x")
            self.admin_separator.pack(fill="x", padx=20, pady=10)
            
            self.os_label.pack(pady=(10, 5), padx=20, fill="x")
            self.nova_os_button.pack(pady=5, padx=20, fill="x")
            self.refresh_os_button.pack(pady=5, padx=20, fill="x")
            self.chat_button.pack(pady=5, padx=20, fill="x")
            self.delete_os_button.pack(pady=5, padx=20, fill="x")
            self.gerenciar_materiais_button.pack(pady=5, padx=20, fill="x")
            
            self.orcamento_label.pack(pady=(20, 5), padx=20, fill="x")
            self.enviar_orcamento_button.pack(pady=5, padx=20, fill="x")
            self.orcamento_separator.pack(fill="x", padx=20, pady=10)
            
            self.estoque_label.pack(pady=(10, 5), padx=20, fill="x")
            self.novo_material_button.pack(pady=5, padx=20, fill="x")
            self.refresh_material_button.pack(pady=5, padx=20, fill="x")
            self.delete_material_button.pack(pady=5, padx=20, fill="x")
            
            # Habilita Botões
            self.user_button.configure(state="normal")
            self.delete_material_button.configure(state="normal")
            self.delete_os_button.configure(state="normal")
            self.gerenciar_materiais_button.configure(state="normal")
            self.enviar_orcamento_button.configure(state="normal")
            self.chat_button.configure(state="normal")
            
            # --- Abas (Ordem: Dashboard -> OS -> Estoque) ---
            self.tab_view.add("Dashboard")
            self.tab_view.add("Ordens de Serviço")
            self.tab_view.add("Estoque")
            
            self.tab_view.set("Dashboard") # Padrão
            
            # Inicializa o conteúdo das abas
            self.create_dashboard_tab(self.tab_view.tab("Dashboard"))
            self.create_os_table(self.tab_view.tab("Ordens de Serviço"))
            self.create_materials_table(self.tab_view.tab("Estoque"))
            
            self.load_materials()
            self.load_os()


        elif perfil == 'proprietario':
            print("View (Main): Acesso de 'Proprietário' concedido.")
            
            # --- Sidebar ---
            self.os_label.pack(pady=(10, 5), padx=20, fill="x")
            self.refresh_os_button.pack(pady=5, padx=20, fill="x")
            self.chat_button.pack(pady=5, padx=20, fill="x")
            
            self.orcamento_label.pack(pady=(20, 5), padx=20, fill="x")
            self.aprovar_orcamento_button.pack(pady=5, padx=20, fill="x")
            self.rejeitar_orcamento_button.pack(pady=5, padx=20, fill="x")

            # Habilita Botões
            self.aprovar_orcamento_button.configure(state="normal")
            self.rejeitar_orcamento_button.configure(state="normal")
            self.chat_button.configure(state="normal")
            
            # --- Abas ---
            self.tab_view.add("Ordens de Serviço")
            self.create_os_table(self.tab_view.tab("Ordens de Serviço"))
            self.load_os()
            
        elif perfil == 'cliente':
            print("View (Main): Acesso de 'Cliente' concedido.")
            
            # --- Sidebar ---
            self.cliente_label.pack(pady=(10, 5), padx=20, fill="x")
            self.nova_solicitacao_button.pack(pady=5, padx=20, fill="x")
            
            self.os_label.pack(pady=(20, 5), padx=20, fill="x")
            self.refresh_os_button.pack(pady=5, padx=20, fill="x")
            self.chat_button.pack(pady=5, padx=20, fill="x")
            
            # Habilita Botões
            self.chat_button.configure(state="normal")
            
            # --- Abas ---
            self.tab_view.add("Ordens de Serviço")
            self.create_os_table(self.tab_view.tab("Ordens de Serviço"))
            self.load_os()
            
        else: 
            print(f"View (Main): Perfil desconhecido '{perfil}'. Bloqueando tudo.")
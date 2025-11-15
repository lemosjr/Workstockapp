import customtkinter as ctk
from tkinter import ttk, messagebox
# Importações das Views
from app.views.estoque_view import EstoqueView
from app.views.os_view import OSView
from app.views.user_view import UserView
from app.views.gerenciar_materiais_view import GerenciarMateriaisView
from app.views.solicitacao_view import SolicitacaoView # Importação para o Cliente
# Importações dos Controllers
from app.controllers import estoque_controller
from app.controllers import os_controller

"""
Camada View (Visão) Principal - A "casca" do aplicativo.
Responsável por exibir a interface principal após o login
e aplicar as permissões de acordo com o perfil do usuário.
"""

class MainView(ctk.CTk):
    
    def __init__(self, user_data):
        super().__init__()
        
        # Armazena os dados do usuário logado (ex: {'id': 1, 'perfil': 'empresa'})
        self.user_data = user_data 
        
        self.title("WorkStock - Gestão de Reformas")
        self.geometry("1200x700")
        
        # Controladores de Janela (para evitar abrir janelas duplicadas)
        self.cadastro_estoque_window = None
        self.cadastro_os_window = None
        self.cadastro_user_window = None
        self.gerenciar_materiais_window = None
        self.solicitacao_window = None 

        self.create_main_widgets()
        
        # Carrega os dados iniciais nas tabelas
        self.load_materials() 
        self.load_os()

        # Aplica as permissões (mostra/esconde botões)
        self._apply_permissions() 

    def create_main_widgets(self):
        # --- Frame Esquerdo (Navegação/Ações) ---
        self.left_frame = ctk.CTkFrame(self, width=200)
        self.left_frame.pack(side="left", fill="y", padx=10, pady=10)
        
        # --- INFO DO USUÁRIO ---
        ctk.CTkLabel(self.left_frame, text="Usuário Logado:", 
                     font=ctk.CTkFont(size=12, weight="bold")).pack(pady=(10, 0))
        
        user_nome = self.user_data.get('nome', 'Usuário') 
        ctk.CTkLabel(self.left_frame, text=user_nome,
                     font=ctk.CTkFont(size=14)).pack(pady=(0, 10))

        user_perfil = self.user_data.get('perfil', 'N/A').capitalize()
        ctk.CTkLabel(self.left_frame, text=f"Perfil: {user_perfil}",
                     font=ctk.CTkFont(size=11)).pack(pady=(0, 10))
        
        # --- SEÇÃO DE ADMINISTRAÇÃO (para 'empresa') ---
        self.admin_label = ctk.CTkLabel(self.left_frame, text="Administração", 
                     font=ctk.CTkFont(size=16, weight="bold"))
        self.admin_label.pack(pady=(10, 0))

        self.user_button = ctk.CTkButton(
            self.left_frame, text="Cadastrar Usuário",
            command=self.abrir_cadastro_usuario, state="disabled"
        )
        self.user_button.pack(pady=10)
        
        self.admin_separator = ctk.CTkFrame(self.left_frame, height=2, fg_color="gray")
        self.admin_separator.pack(fill="x", padx=10, pady=10)

        # --- MÓDULO OS (para 'empresa' e 'proprietario') ---
        self.os_label = ctk.CTkLabel(self.left_frame, text="Módulo OS", font=("Arial", 16))
        self.os_label.pack(pady=10)
        
        self.nova_os_button = ctk.CTkButton(
            self.left_frame, text="Criar Nova OS",
            command=lambda: self.abrir_cadastro_os(os_id=None)
        )
        self.nova_os_button.pack(pady=10)

        self.refresh_os_button = ctk.CTkButton(
            self.left_frame, text="Atualizar Lista de OS", command=self.load_os
        )
        self.refresh_os_button.pack(pady=5)
        
        self.delete_os_button = ctk.CTkButton(
            self.left_frame, text="Deletar OS", command=self._on_delete_os,
            state="disabled", fg_color="#DB3E3E", hover_color="#B73030"
        )
        self.delete_os_button.pack(pady=5)

        self.gerenciar_materiais_button = ctk.CTkButton(
            self.left_frame, text="Gerenciar Materiais da OS",
            command=self._on_gerenciar_materiais, state="disabled"
        )
        self.gerenciar_materiais_button.pack(pady=5)
        
        # --- FLUXO DE ORÇAMENTO (para 'empresa' e 'proprietario') ---
        self.orcamento_label = ctk.CTkLabel(self.left_frame, text="Fluxo de Orçamento:", 
                     font=ctk.CTkFont(size=12, weight="bold"))
        self.orcamento_label.pack(pady=(15, 5))
        
        self.enviar_orcamento_button = ctk.CTkButton(
            self.left_frame, text="Enviar para Aprovação",
            command=self._on_enviar_orcamento, state="disabled"
        )
        self.enviar_orcamento_button.pack(pady=5)

        self.aprovar_orcamento_button = ctk.CTkButton(
            self.left_frame, text="Aprovar Orçamento",
            command=self._on_aprovar_orcamento, state="disabled",
            fg_color="#4CAF50", hover_color="#3B8E40" # Verde
        )
        self.aprovar_orcamento_button.pack(pady=5)
        
        self.rejeitar_orcamento_button = ctk.CTkButton(
            self.left_frame, text="Rejeitar Orçamento",
            command=self._on_rejeitar_orcamento, state="disabled",
            fg_color="#DB3E3E", hover_color="#B73030" # Vermelho
        )
        self.rejeitar_orcamento_button.pack(pady=5)
        
        self.orcamento_separator = ctk.CTkFrame(self.left_frame, height=2, fg_color="gray")
        self.orcamento_separator.pack(fill="x", padx=10, pady=10)

        # --- MÓDULO ESTOQUE (para 'empresa') ---
        self.estoque_label = ctk.CTkLabel(self.left_frame, text="Módulo Estoque", font=("Arial", 16))
        self.estoque_label.pack(pady=10)
        
        self.novo_material_button = ctk.CTkButton(
            self.left_frame, text="Cadastrar Novo Material",
            command=self.abrir_cadastro_material
        )
        self.novo_material_button.pack(pady=10)

        self.refresh_material_button = ctk.CTkButton(
            self.left_frame, text="Atualizar Estoque",
            command=self.load_materials
        )
        self.refresh_material_button.pack(pady=5)

        self.delete_material_button = ctk.CTkButton(
            self.left_frame, text="Deletar Material",
            command=self._on_delete_material, state="disabled",
            fg_color="#DB3E3E", hover_color="#B73030"
        )
        self.delete_material_button.pack(pady=5)
        
        # --- MÓDULO CLIENTE (para 'cliente') ---
        self.cliente_label = ctk.CTkLabel(self.left_frame, text="Minha Conta", 
                     font=ctk.CTkFont(size=16, weight="bold"))
        # (será exibido/oculto via _apply_permissions)

        self.nova_solicitacao_button = ctk.CTkButton(
            self.left_frame, text="Fazer Nova Solicitação",
            command=self.abrir_nova_solicitacao
        )
        # (será exibido/oculto via _apply_permissions)

        # --- Frame Direito (Conteúdo com Abas) ---
        self.tab_view = ctk.CTkTabview(self)
        self.tab_view.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        self.tab_view.add("Ordens de Serviço")
        self.tab_view.add("Estoque")
        self.tab_view.set("Ordens de Serviço") 

        self.create_os_table(self.tab_view.tab("Ordens de Serviço"))
        self.create_materials_table(self.tab_view.tab("Estoque"))

    # --- Métodos de Gestão (Usuário/Admin) ---

    def abrir_cadastro_usuario(self):
        """ Abre a janela de cadastro de Usuário. """
        if self.cadastro_user_window is None or not self.cadastro_user_window.winfo_exists():
            self.cadastro_user_window = UserView(master=self)
        else:
            self.cadastro_user_window.focus()
            
    # --- MÓDULO CLIENTE (Callbacks) ---
    
    def abrir_nova_solicitacao(self):
        """ Abre a janela de solicitação do cliente. """
        if self.solicitacao_window is None or not self.solicitacao_window.winfo_exists():
            self.solicitacao_window = SolicitacaoView(master=self)
            # Quando a janela fechar, atualiza a lista de OS
            self.solicitacao_window.bind("<Destroy>", self.on_solicitacao_closed)
        else:
            self.solicitacao_window.focus()

    def on_solicitacao_closed(self, event):
        """ Chamado quando a janela SolicitacaoView fecha. """
        if event.widget == self.solicitacao_window:
            print("View (Main): Janela de solicitação fechada. Atualizando lista de OS...")
            self.load_os()

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
        """ Cria a tabela (Treeview) para exibir os materiais. """
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background="#2b2b2b", foreground="#dce4ee", fieldbackground="#343638", rowheight=25, borderwidth=0)
        style.map('Treeview', background=[('selected', '#3471CD')])
        style.configure("Treeview.Heading", background="#565B5E", foreground="#dce4ee", font=("Arial", 10, "bold"), relief="flat")
        style.map("Treeview.Heading", background=[('active', '#343638')])
        columns = ("id", "sku", "nome", "estoque_atual", "preco_custo", "unidade_medida")
        self.estoque_tree = ttk.Treeview(parent_frame, columns=columns, show="headings")
        self.estoque_tree.heading("id", text="ID"); self.estoque_tree.heading("sku", text="SKU"); self.estoque_tree.heading("nome", text="Nome"); self.estoque_tree.heading("estoque_atual", text="Estoque"); self.estoque_tree.heading("preco_custo", text="Preço (R$)"); self.estoque_tree.heading("unidade_medida", text="Un.")
        self.estoque_tree.column("id", width=40, anchor="center"); self.estoque_tree.column("sku", width=100); self.estoque_tree.column("nome", width=250); self.estoque_tree.column("estoque_atual", width=60, anchor="center"); self.estoque_tree.column("preco_custo", width=80, anchor="e"); self.estoque_tree.column("unidade_medida", width=50, anchor="center")
        self.estoque_tree.pack(fill="both", expand=True, padx=10, pady=10)

    def load_materials(self):
        """ Carrega os materiais do controller para a tabela. """
        for item in self.estoque_tree.get_children(): self.estoque_tree.delete(item)
        sucesso, dados = estoque_controller.listar_materiais()
        if sucesso:
            for material in dados:
                valores = (material['id'], material['sku'], material['nome'], material['estoque_atual'], f"{material['preco_custo']:.2f}", material['unidade_medida'])
                self.estoque_tree.insert("", "end", values=valores)
        else:
            messagebox.showerror("Erro", "Não foi possível carregar a lista de materiais.")

    def abrir_cadastro_material(self):
        """ Abre a janela de cadastro de material. """
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

    def _get_selected_os_id(self):
        """Função helper para pegar o ID da OS selecionada na tabela."""
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
        """ Chamado pelo botão "Deletar OS". """
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
        """ Chamado pelo botão "Gerenciar Materiais da OS". """
        os_id = self._get_selected_os_id()
        if not os_id: return
        print(f"View (Main): Abrindo gerenciador de materiais para OS #{os_id}")
        if self.gerenciar_materiais_window is None or not self.gerenciar_materiais_window.winfo_exists():
            self.gerenciar_materiais_window = GerenciarMateriaisView(master=self, os_id=os_id)
            self.gerenciar_materiais_window.bind("<Destroy>", self.on_materiais_closed)
        else:
            self.gerenciar_materiais_window.focus()

    def on_materiais_closed(self, event):
        """ Chamado quando a janela GerenciarMateriaisView é fechada. """
        if event.widget == self.gerenciar_materiais_window:
            print("View (Main): Janela de materiais fechada. Atualizando listas...")
            self.load_materials()
            self.load_os()

    # --- Funções de Fluxo de Orçamento ---
    
    def _on_enviar_orcamento(self):
        """ Chamado pelo botão "Enviar para Aprovação". """
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
        """ Chamado pelo botão "Aprovar Orçamento". """
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
        """ Chamado pelo botão "Rejeitar Orçamento". """
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

    # --- Funções das Tabelas ---

    def create_os_table(self, parent_frame):
        """ Cria a tabela (Treeview) para exibir as OS. """
        columns = ("id", "status", "prioridade", "tipo_servico", "endereco", "data_abertura", "data_prevista")
        self.os_tree = ttk.Treeview(parent_frame, columns=columns, show="headings")
        self.os_tree.heading("id", text="OS #"); self.os_tree.heading("status", text="Status"); self.os_tree.heading("prioridade", text="Prioridade"); self.os_tree.heading("tipo_servico", text="Serviço"); self.os_tree.heading("endereco", text="Endereço"); self.os_tree.heading("data_abertura", text="Data Abertura"); self.os_tree.heading("data_prevista", text="Previsão Entrega")
        self.os_tree.column("id", width=50, anchor="center"); self.os_tree.column("status", width=120); self.os_tree.column("prioridade", width=80); self.os_tree.column("tipo_servico", width=150); self.os_tree.column("endereco", width=250); self.os_tree.column("data_abertura", width=130, anchor="center"); self.os_tree.column("data_prevista", width=130, anchor="center")
        self.os_tree.pack(fill="both", expand=True, padx=10, pady=10)
        self.os_tree.bind("<Double-1>", self._on_os_double_click)

    def load_os(self):
        """ Carrega as OSs do controller para a tabela. """
        print("View: Solicitando lista de OS ao Controller...")
        for item in self.os_tree.get_children(): self.os_tree.delete(item)
        sucesso, dados = os_controller.listar_os()
        if sucesso:
            print(f"View: Recebeu {len(dados)} Ordens de Serviço.")
            for os in dados:
                data_abertura_fmt = os['data_abertura'].strftime('%d/%m/%Y %H:%M')
                data_prevista_fmt = os['data_conclusao_prevista'].strftime('%d/%m/%Y') if os['data_conclusao_prevista'] else "---"
                valores = (os['id'], os['status'].capitalize(), os['prioridade'].capitalize(), os['tipo_servico'], os['endereco'], data_abertura_fmt, data_prevista_fmt)
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
        os_id = self._get_selected_os_id()
        if not os_id: return
        print(f"View (Main): Duplo-clique detectado. Abrindo edição para OS #{os_id}")
        self.abrir_cadastro_os(os_id=os_id)

    def on_os_cadastro_closed(self, event):
        """ Chamado quando a janela de cadastro de OS fecha. """
        if event.widget == self.cadastro_os_window:
            print("View: Janela de OS fechada. Atualizando lista...")
            self.load_os()
            
    # --- Método de Permissões (O CÉREBRO DA UI) ---

    def _apply_permissions(self):
        """ 
        Ajusta a UI com base no perfil do usuário logado.
        Esta é a implementação de "Segurança por Padrão".
        """
        
        perfil = self.user_data.get('perfil')
        print(f"View (Main): Aplicando permissões para o perfil: '{perfil}'")

        # --- 1. ESCONDE TUDO PRIMEIRO ---
        # (Esconde todos os widgets que dependem de permissão)
        self.admin_label.pack_forget()
        self.user_button.pack_forget()
        self.admin_separator.pack_forget()
        self.os_label.pack_forget()
        self.nova_os_button.pack_forget()
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
        
        try: # Esconde a aba de Estoque
            self.tab_view.delete("Estoque")
        except Exception:
            pass # Ignora erro se já foi removida


        # --- 2. HABILITA SEÇÕES COM BASE NO PERFIL ---
        
        if perfil == 'empresa':
            print("View (Main): Acesso de 'Empresa' concedido.")
            # Re-exibe os widgets da EMPRESA na ordem correta
            self.admin_label.pack(pady=(10, 0))
            self.user_button.pack(pady=10)
            self.admin_separator.pack(fill="x", padx=10, pady=10)
            
            self.os_label.pack(pady=10)
            self.nova_os_button.pack(pady=10)
            self.refresh_os_button.pack(pady=5) # (Refresh é quase universal)
            self.delete_os_button.pack(pady=5)
            self.gerenciar_materiais_button.pack(pady=5)
            
            self.orcamento_label.pack(pady=(15, 5))
            self.enviar_orcamento_button.pack(pady=5)
            self.orcamento_separator.pack(fill="x", padx=10, pady=10)
            
            self.estoque_label.pack(pady=10)
            self.novo_material_button.pack(pady=10)
            self.refresh_material_button.pack(pady=5)
            self.delete_material_button.pack(pady=5)
            
            # Habilita os botões (estado já foi definido na criação)
            self.user_button.configure(state="normal")
            self.delete_material_button.configure(state="normal")
            self.delete_os_button.configure(state="normal")
            self.gerenciar_materiais_button.configure(state="normal")
            self.enviar_orcamento_button.configure(state="normal")
            
            # Re-adiciona a aba de Estoque
            self.tab_view.add("Estoque")
            # Precisamos recriar os widgets da aba se ela foi removida
            self.create_materials_table(self.tab_view.tab("Estoque"))
            self.load_materials()


        elif perfil == 'proprietario':
            print("View (Main): Acesso de 'Proprietário' concedido.")
            # Re-exibe os widgets do PROPRIETÁRIO
            self.os_label.pack(pady=10)
            self.refresh_os_button.pack(pady=5) # Pode atualizar a lista
            
            self.orcamento_label.pack(pady=(15, 5))
            self.aprovar_orcamento_button.pack(pady=5)
            self.rejeitar_orcamento_button.pack(pady=5)

            # Habilita os botões
            self.aprovar_orcamento_button.configure(state="normal")
            self.rejeitar_orcamento_button.configure(state="normal")
            
        elif perfil == 'cliente':
            print("View (Main): Acesso de 'Cliente' concedido.")
            # Re-exibe os widgets do CLIENTE
            self.cliente_label.pack(pady=(10, 0))
            self.nova_solicitacao_button.pack(pady=10)
            self.refresh_os_button.pack(pady=5) # Pode atualizar a lista
            
        else: # Perfil desconhecido (segurança)
            print(f"View (Main): Perfil desconhecido '{perfil}'. Bloqueando tudo.")
            try: # Esconde a aba de OS também
                self.tab_view.delete("Ordens de Serviço")
            except Exception:
                pass
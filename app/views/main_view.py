import customtkinter as ctk
from app.views.estoque_view import EstoqueView
from app.controllers import estoque_controller # Precisamos importar o controller
from tkinter import ttk # Importamos o Treeview (tabela)
from tkinter import messagebox

"""
Camada View (Visão) Principal - A "casca" do aplicativo.
"""

class MainView(ctk.CTk):
    
    def __init__(self):
        super().__init__()
        
        self.title("WorkStock - Gestão de Reformas")
        self.geometry("1000x600") # Aumentei a largura para a tabela
        
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        self.create_main_widgets()
        
        self.cadastro_estoque_window = None
        
        # Carrega os materiais assim que o app inicia
        self.load_materials() 

    def create_main_widgets(self):
        # --- Frame Esquerdo (Navegação/Ações) ---
        left_frame = ctk.CTkFrame(self, width=200)
        left_frame.pack(side="left", fill="y", padx=10, pady=10)

        ctk.CTkLabel(left_frame, text="Ações de Estoque", font=("Arial", 16)).pack(pady=10)
        
        estoque_button = ctk.CTkButton(
            left_frame, 
            text="Cadastrar Novo Material",
            command=self.abrir_cadastro_material
        )
        estoque_button.pack(pady=10)

        refresh_button = ctk.CTkButton(
            left_frame,
            text="Atualizar Lista",
            command=self.load_materials # Conecta ao novo método
        )
        refresh_button.pack(pady=10)

        # --- Frame Direito (Conteúdo / Tabela) ---
        right_frame = ctk.CTkFrame(self)
        right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(right_frame, text="Materiais em Estoque", font=("Arial", 16)).pack(pady=10)

        self.create_materials_table(right_frame)

    def create_materials_table(self, parent_frame):
        """
        Cria a tabela (Treeview) para exibir os materiais.
        """
        # --- Configuração de Estilo do Treeview ---
        # (Isso é um pouco avançado, mas essencial para o visual)
        style = ttk.Style()
        style.theme_use("default") # Usamos default para poder sobrescrever

        # Configura as cores do Treeview para combinar com o CustomTkinter
        # (Adapte as cores "fg_color" e "text_color" se usar um tema diferente)
        style.configure("Treeview", 
                        background="#2b2b2b", # Cor de fundo do frame do CTk
                        foreground="#dce4ee", # Cor do texto do CTk
                        fieldbackground="#343638", # Cor de fundo do entry do CTk
                        rowheight=25,
                        bordercolor="#565B5E",
                        borderwidth=0)
        style.map('Treeview', background=[('selected', '#3471CD')]) # Cor de seleção
        
        style.configure("Treeview.Heading", 
                        background="#565B5E", # Cor do cabeçalho
                        foreground="#dce4ee",
                        font=("Arial", 10, "bold"),
                        relief="flat")
        style.map("Treeview.Heading", 
                  background=[('active', '#343638')])

        # --- Criação do Treeview ---
        
        # Definimos as colunas que queremos
        columns = ("id", "sku", "nome", "estoque_atual", "preco_custo", "unidade_medida")
        
        self.tree = ttk.Treeview(parent_frame, columns=columns, show="headings")
        
        # Definindo os cabeçalhos
        self.tree.heading("id", text="ID")
        self.tree.heading("sku", text="SKU")
        self.tree.heading("nome", text="Nome")
        self.tree.heading("estoque_atual", text="Estoque")
        self.tree.heading("preco_custo", text="Preço (R$)")
        self.tree.heading("unidade_medida", text="Un.")
        
        # Definindo a largura das colunas
        self.tree.column("id", width=40, anchor="center")
        self.tree.column("sku", width=100)
        self.tree.column("nome", width=250)
        self.tree.column("estoque_atual", width=60, anchor="center")
        self.tree.column("preco_custo", width=80, anchor="e") # 'e' = right-align
        self.tree.column("unidade_medida", width=50, anchor="center")
        
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

    def load_materials(self):
        """
        Busca os dados no Controller e atualiza a tabela (Treeview).
        """
        print("View: Solicitando lista de materiais ao Controller...")
        
        # 1. Limpa a tabela antes de carregar
        # (Itera e deleta todos os 'filhos' da raiz)
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # 2. Chama o Controller
        sucesso, dados = estoque_controller.listar_materiais()
        
        # 3. Processa a resposta
        if sucesso:
            print(f"View: Recebeu {len(dados)} materiais.")
            # 4. Preenche a tabela
            for material in dados:
                # O 'material' é um dicionário (graças ao DictCursor que usamos no Model)
                valores = (
                    material['id'],
                    material['sku'],
                    material['nome'],
                    material['estoque_atual'],
                    f"{material['preco_custo']:.2f}", # Formata o preço
                    material['unidade_medida']
                )
                self.tree.insert("", "end", values=valores)
        else:
            print("View: Erro ao carregar materiais.")
            messagebox.showerror("Erro", "Não foi possível carregar a lista de materiais.")

    def abrir_cadastro_material(self):
        """
        Abre a janela de cadastro de material.
        """
        if self.cadastro_estoque_window is None or not self.cadastro_estoque_window.winfo_exists():
            self.cadastro_estoque_window = EstoqueView(master=self)
            
            # --- MELHORIA ---
            # Faz a janela de cadastro "avisar" a principal quando fechar,
            # para que a lista seja atualizada automaticamente.
            self.cadastro_estoque_window.bind("<Destroy>", self.on_cadastro_closed)
            
        else:
            self.cadastro_estoque_window.focus()

    def on_cadastro_closed(self, event):
        """
        Chamado automaticamente quando a janela de cadastro é fechada.
        """
        # Verificamos se o evento veio da janela Toplevel (e não de um widget interno)
        if event.widget == self.cadastro_estoque_window:
            print("View: Janela de cadastro fechada. Atualizando lista...")
            self.load_materials()
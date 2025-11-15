import customtkinter as ctk
from app.controllers import estoque_controller
from tkinter import messagebox # Usaremos para exibir pop-ups de sucesso/erro

"""
Camada View (Visão) para Cadastro de Estoque.

Responsabilidade:
- Exibir a interface gráfica (widgets) para o usuário.
- Capturar a entrada do usuário (cliques, digitação).
- Chamar o Controller quando uma ação de negócio for necessária (ex: salvar).
- Exibir retornos (sucesso, erro) do Controller para o usuário.
- NÃO deve conter lógica de negócio ou SQL.
"""

class EstoqueView(ctk.CTkToplevel):
    
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Cadastrar Novo Material")
        self.geometry("400x500")
        
        # Faz com que esta janela fique "na frente" da principal
        self.transient(master)
        self.grab_set()
        
        self.create_widgets()

    def create_widgets(self):
        # Frame principal para organizar os campos
        frame = ctk.CTkFrame(self)
        frame.pack(padx=20, pady=20, fill="both", expand=True)

        # --- Campos do Formulário ---
        # Baseado nos requisitos
        
        ctk.CTkLabel(frame, text="Nome do Material:*").pack(anchor="w")
        self.nome_entry = ctk.CTkEntry(frame, width=300)
        self.nome_entry.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(frame, text="SKU:*").pack(anchor="w")
        self.sku_entry = ctk.CTkEntry(frame, width=300)
        self.sku_entry.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(frame, text="Unidade de Medida:").pack(anchor="w")
        self.unidade_entry = ctk.CTkEntry(frame, width=300)
        self.unidade_entry.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(frame, text="Preço de Custo (Ex: 12.50):").pack(anchor="w")
        self.preco_entry = ctk.CTkEntry(frame, width=300)
        self.preco_entry.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(frame, text="Estoque Atual:").pack(anchor="w")
        self.estoque_entry = ctk.CTkEntry(frame, width=300)
        self.estoque_entry.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(frame, text="Estoque Mínimo:").pack(anchor="w")
        self.estoque_min_entry = ctk.CTkEntry(frame, width=300)
        self.estoque_min_entry.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(frame, text="Fornecedor:").pack(anchor="w")
        self.fornecedor_entry = ctk.CTkEntry(frame, width=300)
        self.fornecedor_entry.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(frame, text="Localização:").pack(anchor="w")
        self.localizacao_entry = ctk.CTkEntry(frame, width=300)
        self.localizacao_entry.pack(fill="x", pady=(0, 10))

        # --- Botão Salvar ---
        save_button = ctk.CTkButton(frame, text="Salvar Material", command=self.salvar)
        save_button.pack(pady=20, side="bottom")

    def salvar(self):
        """
        Coleta os dados da interface e envia para o Controller.
        """
        # 1. Coletar dados da View
        data = {
            "nome": self.nome_entry.get(),
            "sku": self.sku_entry.get(),
            "unidade_medida": self.unidade_entry.get(),
            "preco_custo": self.preco_entry.get() or None,
            "estoque_atual": self.estoque_entry.get() or None,
            "estoque_minimo": self.estoque_min_entry.get() or None,
            "fornecedor": self.fornecedor_entry.get(),
            "localizacao": self.localizacao_entry.get()
        }
        
        print(f"View: Coletou dados do formulário: {data}")

        # 2. Enviar dados para o Controller
        # A View NÃO SABE o que acontece. Ela só chama o Controller.
        sucesso, mensagem = estoque_controller.salvar_material(data)
        
        # 3. Exibir resposta do Controller para o usuário
        if sucesso:
            messagebox.showinfo("Sucesso", mensagem)
            self.destroy() # Fecha a janela de cadastro
        else:
            messagebox.showerror("Erro", mensagem)
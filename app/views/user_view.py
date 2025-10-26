import customtkinter as ctk
from app.controllers import user_controller # O novo controller
from tkinter import messagebox

"""
Camada View (Visão) para Cadastro de Usuário.

Responsabilidade:
- Exibir a interface gráfica (widgets) para o usuário (admin).
- Capturar a entrada (dados do novo usuário).
- Chamar o User_Controller quando a ação de salvar for necessária.
"""

class UserView(ctk.CTkToplevel):
    
    def __init__(self, master=None):
        super().__init__(master)
        
        self.title("Cadastrar Novo Usuário")
        self.geometry("400x550")
        
        self.transient(master) # Mantém esta janela na frente
        self.grab_set() # Torna a janela "modal"
        
        # Lista de perfis (do ENUM do DB / Controller)
        self.profile_list = ['empresa', 'proprietario', 'cliente']
        
        self.create_widgets()

    def create_widgets(self):
        frame = ctk.CTkFrame(self)
        frame.pack(padx=20, pady=20, fill="both", expand=True)

        ctk.CTkLabel(frame, text="Novo Usuário", 
                     font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(0, 15))

        # --- Campos do Formulário ---
        
        ctk.CTkLabel(frame, text="Nome Completo:*").pack(anchor="w")
        self.nome_entry = ctk.CTkEntry(frame, width=300)
        self.nome_entry.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(frame, text="E-mail:*").pack(anchor="w")
        self.email_entry = ctk.CTkEntry(frame, width=300)
        self.email_entry.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(frame, text="Perfil do Usuário:*").pack(anchor="w")
        self.perfil_combo = ctk.CTkComboBox(frame, width=300, values=self.profile_list)
        self.perfil_combo.set('cliente') # Define 'cliente' como padrão
        self.perfil_combo.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(frame, text="Senha (mín. 6 caracteres):*").pack(anchor="w")
        self.senha_entry = ctk.CTkEntry(frame, width=300, show="*")
        self.senha_entry.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(frame, text="Confirmar Senha:*").pack(anchor="w")
        self.confirma_senha_entry = ctk.CTkEntry(frame, width=300, show="*")
        self.confirma_senha_entry.pack(fill="x", pady=(0, 10))

        # --- Botão Salvar ---
        save_button = ctk.CTkButton(frame, text="Salvar Novo Usuário", 
                                    command=self.salvar)
        save_button.pack(pady=20, side="bottom")

    def salvar(self):
        """
        Coleta os dados da interface e envia para o User_Controller.
        """
        # 1. Coletar dados da View
        data = {
            "nome": self.nome_entry.get(),
            "email": self.email_entry.get(),
            "senha": self.senha_entry.get(),
            "confirma_senha": self.confirma_senha_entry.get(),
            "perfil": self.perfil_combo.get()
        }
        
        print(f"View (User): Coletou dados do formulário para: {data.get('email')}")

        # 2. Enviar dados para o Controller
        # A View não valida, apenas envia. O Controller faz a mágica.
        sucesso, mensagem = user_controller.register_user(data)
        
        # 3. Exibir resposta
        if sucesso:
            messagebox.showinfo("Sucesso", mensagem)
            self.destroy() # Fecha a janela de cadastro
        else:
            messagebox.showerror("Erro de Validação", mensagem)
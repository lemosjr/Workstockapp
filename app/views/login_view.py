import customtkinter as ctk
from app.controllers import auth_controller
from tkinter import messagebox

"""
Camada View (Visão) para Login.

Responsabilidade:
- É a janela principal (raiz) inicial da aplicação.
- Coleta credenciais (e-mail e senha).
- Chama o Auth_Controller para validar o login.
- Define "flags" para o main.py saber se o login foi bem-sucedido.
"""

class LoginView(ctk.CTk):
    
    def __init__(self):
        super().__init__()
        
        self.title("WorkStock - Acesso ao Sistema")
        self.geometry("380x420")
        self.resizable(False, False) # Impede de redimensionar
        self.protocol("WM_DELETE_WINDOW", self._on_closing) # Intercepta o "X"

        # --- Flags de Resultado ---
        # main.py irá verificar estes valores após a janela fechar
        self.login_successful = False
        self.user_data = None # Armazena os dados do usuário (id, nome, perfil)

        self._create_widgets()

    def _create_widgets(self):
        # Frame principal
        frame = ctk.CTkFrame(self)
        frame.pack(padx=30, pady=30, fill="both", expand=True)

        ctk.CTkLabel(frame, text="WorkStock Login", 
                     font=ctk.CTkFont(size=24, weight="bold")).pack(pady=20)

        # --- Campo E-mail ---
        ctk.CTkLabel(frame, text="E-mail:").pack(anchor="w", padx=10)
        self.email_entry = ctk.CTkEntry(frame, width=300)
        self.email_entry.pack(pady=(0, 15))
        
        # --- Campo Senha ---
        ctk.CTkLabel(frame, text="Senha:").pack(anchor="w", padx=10)
        self.senha_entry = ctk.CTkEntry(frame, width=300, show="*")
        self.senha_entry.pack(pady=(0, 20))
        
        # --- Botão Entrar ---
        self.login_button = ctk.CTkButton(frame, text="Entrar", 
                                          command=self._on_login_click)
        self.login_button.pack(pady=10, fill="x")

        # --- Bind (atalho) da tecla Enter ---
        # Permite que o usuário pressione Enter no campo de senha
        self.senha_entry.bind("<Return>", self._on_login_click)

        # --- Dados de Teste (Para facilitar o desenvolvimento) ---
        # (Você pode comentar ou apagar estas linhas)
        self.email_entry.insert(0, "admin@empresa.com")
        self.senha_entry.insert(0, "admin123")

    def _on_login_click(self, event=None): # 'event=None' é necessário para o bind
        """
        Chamado pelo clique no botão ou pela tecla Enter.
        """
        email = self.email_entry.get()
        senha = self.senha_entry.get()

        print("View (Login): Tentando login...")

        # 2. Enviar para o Controller
        sucesso, data_or_msg = auth_controller.login(email, senha)
        
        # 3. Processar a resposta
        if sucesso:
            # Login bem-sucedido!
            print("View (Login): Login OK.")
            messagebox.showinfo("Sucesso", f"Bem-vindo, {data_or_msg['nome']}!")
            
            # Define as flags que o main.py irá ler
            self.login_successful = True
            self.user_data = data_or_msg
            
            # Fecha a janela de login
            self.destroy() 
        else:
            # Falha no login
            print(f"View (Login): Falha no login. {data_or_msg}")
            messagebox.showerror("Erro de Login", data_or_msg)

    def _on_closing(self):
        """
        Chamado quando o usuário clica no "X" da janela.
        Garante que o app saiba que o login foi cancelado.
        """
        self.login_successful = False
        self.destroy()
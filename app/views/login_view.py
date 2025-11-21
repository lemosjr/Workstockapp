import customtkinter as ctk
from app.controllers import auth_controller
from tkinter import messagebox

# --- PALETA DE CORES ---
COLOR_PRIMARY = "#264653"   # Teal Escuro (Fundo do Card)
COLOR_ACCENT = "#F2B263"    # Laranja (Botão Principal)
COLOR_ACCENT_HOVER = "#D9A059" 
COLOR_TEXT_LIGHT = "#F2F2F2" # Texto Claro
COLOR_TEXT_DARK = "#264653"  # Texto Escuro (Para contraste no botão laranja)

class LoginView(ctk.CTk):
    
    def __init__(self):
        super().__init__()
        
        self.title("WorkStock - Login")
        self.geometry("400x480")
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self._on_closing)

        self.login_successful = False
        self.user_data = None

        # Configura o fundo da janela principal para um tom neutro/escuro
        self._set_appearance_mode("Dark") 
        
        self._create_widgets()

    def _create_widgets(self):
        # Fundo principal centralizado
        bg_frame = ctk.CTkFrame(self, fg_color="transparent")
        bg_frame.pack(fill="both", expand=True)

        # Card de Login (Com a cor Teal Escuro #264653)
        card_frame = ctk.CTkFrame(
            bg_frame, 
            fg_color=COLOR_PRIMARY, 
            corner_radius=20,
            border_color=COLOR_ACCENT,
            border_width=2
        )
        card_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.85, relheight=0.75)

        # Título
        ctk.CTkLabel(
            card_frame, 
            text="WorkStock", 
            font=("Roboto Medium", 28),
            text_color=COLOR_ACCENT
        ).pack(pady=(40, 5))
        
        ctk.CTkLabel(
            card_frame, 
            text="Gestão de Reformas", 
            font=("Roboto", 14),
            text_color=COLOR_TEXT_LIGHT
        ).pack(pady=(0, 30))

        # Campo E-mail
        self.email_entry = ctk.CTkEntry(
            card_frame, 
            width=280, 
            height=40,
            placeholder_text="E-mail",
            fg_color=COLOR_TEXT_LIGHT,
            text_color=COLOR_TEXT_DARK,
            border_color="white"
        )
        self.email_entry.pack(pady=(0, 15))
        
        # Campo Senha
        self.senha_entry = ctk.CTkEntry(
            card_frame, 
            width=280, 
            height=40,
            show="*",
            placeholder_text="Senha",
            fg_color=COLOR_TEXT_LIGHT,
            text_color=COLOR_TEXT_DARK,
            border_color="white"
        )
        self.senha_entry.pack(pady=(0, 25))
        
        # Botão Entrar (Laranja #F2B263)
        self.login_button = ctk.CTkButton(
            card_frame, 
            text="ENTRAR", 
            width=280, 
            height=45,
            font=("Roboto Medium", 14),
            fg_color=COLOR_ACCENT,
            hover_color=COLOR_ACCENT_HOVER,
            text_color=COLOR_TEXT_DARK, # Texto escuro para contraste no laranja
            command=self._on_login_click
        )
        self.login_button.pack(pady=10)

        self.senha_entry.bind("<Return>", self._on_login_click)

        # Dados de teste (opcional)
        self.email_entry.insert(0, "empresa@gmail.com")
        self.senha_entry.insert(0, "123456")

    def _on_login_click(self, event=None):
        email = self.email_entry.get()
        senha = self.senha_entry.get()
        sucesso, data_or_msg = auth_controller.login(email, senha)
        
        if sucesso:
            self.login_successful = True
            self.user_data = data_or_msg
            self.destroy() 
        else:
            messagebox.showerror("Erro de Login", data_or_msg)

    def _on_closing(self):
        self.login_successful = False
        self.destroy()
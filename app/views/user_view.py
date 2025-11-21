import customtkinter as ctk
from app.controllers import user_controller
from tkinter import messagebox

# --- PALETA DE CORES ---
COLOR_PRIMARY = "#264653"
COLOR_ACCENT = "#F2B263"
COLOR_ACCENT_HOVER = "#D9A059"
COLOR_TEXT_DARK = "#264653"

class UserView(ctk.CTkToplevel):
    
    def __init__(self, master=None):
        super().__init__(master)
        
        self.title("Cadastrar Novo Usuário")
        self.geometry("400x600")
        self.transient(master)
        self.grab_set()
        
        self.profile_list = ['empresa', 'proprietario', 'cliente']
        self.create_widgets()

    def create_widgets(self):
        # --- Cabeçalho ---
        header_frame = ctk.CTkFrame(self, height=60, corner_radius=0, fg_color=COLOR_PRIMARY)
        header_frame.pack(fill="x", side="top")
        
        ctk.CTkLabel(header_frame, text="Novo Usuário", 
                     font=("Roboto Medium", 20), text_color="white").pack(pady=15)

        # --- Corpo ---
        body_frame = ctk.CTkFrame(self, fg_color="transparent")
        body_frame.pack(fill="both", expand=True, padx=30, pady=30)

        self._add_label(body_frame, "Nome Completo:*")
        self.nome_entry = ctk.CTkEntry(body_frame, height=35)
        self.nome_entry.pack(fill="x", pady=(0, 15))

        self._add_label(body_frame, "E-mail:*")
        self.email_entry = ctk.CTkEntry(body_frame, height=35)
        self.email_entry.pack(fill="x", pady=(0, 15))
        
        self._add_label(body_frame, "Perfil do Usuário:*")
        self.perfil_combo = ctk.CTkComboBox(body_frame, values=self.profile_list, height=35, button_color=COLOR_PRIMARY)
        self.perfil_combo.set('cliente')
        self.perfil_combo.pack(fill="x", pady=(0, 15))

        self._add_label(body_frame, "Senha (mín. 6 caracteres):*")
        self.senha_entry = ctk.CTkEntry(body_frame, height=35, show="*")
        self.senha_entry.pack(fill="x", pady=(0, 15))
        
        self._add_label(body_frame, "Confirmar Senha:*")
        self.confirma_senha_entry = ctk.CTkEntry(body_frame, height=35, show="*")
        self.confirma_senha_entry.pack(fill="x", pady=(0, 15))

        # --- Botão Salvar ---
        save_button = ctk.CTkButton(
            body_frame, 
            text="CADASTRAR", 
            height=45,
            font=("Roboto Medium", 14),
            fg_color=COLOR_ACCENT, 
            hover_color=COLOR_ACCENT_HOVER, 
            text_color=COLOR_TEXT_DARK,
            command=self.salvar
        )
        save_button.pack(fill="x", pady=(20, 0))

    def _add_label(self, parent, text):
        ctk.CTkLabel(parent, text=text, font=("Roboto", 12, "bold"), text_color="gray").pack(anchor="w", pady=(0, 2))

    def salvar(self):
        data = {
            "nome": self.nome_entry.get(),
            "email": self.email_entry.get(),
            "senha": self.senha_entry.get(),
            "confirma_senha": self.confirma_senha_entry.get(),
            "perfil": self.perfil_combo.get()
        }
        sucesso, mensagem = user_controller.register_user(data)
        if sucesso:
            messagebox.showinfo("Sucesso", mensagem)
            self.destroy()
        else:
            messagebox.showerror("Erro", mensagem)
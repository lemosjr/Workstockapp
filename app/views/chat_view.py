import customtkinter as ctk
from app.controllers import chat_controller
from tkinter import messagebox

"""
Camada View (Visão) para o Chat da OS.

Responsabilidade:
- Exibir histórico de mensagens com rolagem.
- Permitir envio de novas mensagens.
- Diferenciar visualmente mensagens do usuário atual vs. outros.
"""

class ChatView(ctk.CTkToplevel):
    
    def __init__(self, master, os_id, current_user_id):
        super().__init__(master)
        
        self.os_id = os_id
        self.current_user_id = current_user_id # ID de quem está logado
        
        self.title(f"Chat - Ordem de Serviço #{self.os_id}")
        self.geometry("500x600")
        
        self.transient(master)
        # Não usamos grab_set() aqui para permitir que o usuário 
        # consulte outras janelas enquanto vê o chat.
        
        self.create_widgets()
        self.load_chat()

    def create_widgets(self):
        # --- Área de Histórico (Rolagem) ---
        self.history_frame = ctk.CTkScrollableFrame(self, width=460, height=480)
        self.history_frame.pack(pady=10, padx=10, fill="both", expand=True)
        
        # --- Área de Envio ---
        input_frame = ctk.CTkFrame(self, height=50)
        input_frame.pack(fill="x", padx=10, pady=10, side="bottom")
        
        self.msg_entry = ctk.CTkEntry(input_frame, placeholder_text="Digite sua mensagem...")
        self.msg_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.msg_entry.bind("<Return>", self._on_send) # Enter envia
        
        send_button = ctk.CTkButton(input_frame, text="Enviar", width=80, command=self._on_send)
        send_button.pack(side="right")
        
        # Botão de Atualizar (Manual)
        refresh_btn = ctk.CTkButton(self, text="Atualizar", width=60, height=20, 
                                    fg_color="gray", command=self.load_chat)
        refresh_btn.place(relx=0.95, rely=0.02, anchor="ne")

    def load_chat(self):
        """
        Busca mensagens e preenche o frame de histórico.
        """
        # Limpa as mensagens antigas da tela
        for widget in self.history_frame.winfo_children():
            widget.destroy()
            
        sucesso, mensagens = chat_controller.buscar_chat_os(self.os_id)
        
        if sucesso:
            for msg in mensagens:
                self._add_message_bubble(msg)
                
            # Rola para o final (mensagem mais recente)
            # (O CustomTkinter não tem um método .see() perfeito para scrollable frame,
            #  mas adicionar os widgets no fim já ajuda).
        else:
            pass # Erro silencioso ou log

    def _add_message_bubble(self, msg):
        """
        Cria o visual de uma única mensagem (o "balão").
        """
        eh_minha = (msg['remetente_id'] == self.current_user_id)
        
        # Configuração visual (Alinhamento e Cor)
        if eh_minha:
            align = "e" # East (Direita)
            bubble_color = "#3B8ED0" # Azul padrão
            text_color = "white"
            anchor_frame = "e"
        else:
            align = "w" # West (Esquerda)
            bubble_color = "#444444" # Cinza escuro
            text_color = "#DCE4EE"
            anchor_frame = "w"

        # Container da mensagem
        container = ctk.CTkFrame(self.history_frame, fg_color="transparent")
        container.pack(fill="x", pady=5, anchor=anchor_frame)
        
        # Balão colorido
        bubble = ctk.CTkFrame(container, fg_color=bubble_color, corner_radius=15)
        bubble.pack(anchor=anchor_frame, padx=10) # O pack define o lado
        
        # Cabeçalho (Nome - Data)
        header_text = f"{msg['nome']} ({msg['perfil']})"
        if not eh_minha: # Só mostra nome se não for eu
            header_lbl = ctk.CTkLabel(bubble, text=header_text, 
                                      font=("Arial", 10, "bold"), text_color=text_color)
            header_lbl.pack(anchor="w", padx=10, pady=(5, 0))
        
        # Texto da Mensagem
        # Usamos 'wraplength' para quebrar linhas se o texto for longo
        msg_lbl = ctk.CTkLabel(bubble, text=msg['texto'], 
                               font=("Arial", 12), text_color=text_color,
                               wraplength=350, justify="left")
        msg_lbl.pack(padx=10, pady=5)
        
        # Rodapé (Hora)
        time_lbl = ctk.CTkLabel(bubble, text=msg['data'], 
                                font=("Arial", 9), text_color="#DDDDDD")
        time_lbl.pack(anchor="e", padx=10, pady=(0, 5))

    def _on_send(self, event=None):
        texto = self.msg_entry.get()
        if not texto.strip(): return
        
        # Envia
        sucesso, msg = chat_controller.enviar_mensagem(self.os_id, self.current_user_id, texto)
        
        if sucesso:
            self.msg_entry.delete(0, "end") # Limpa campo
            self.load_chat() # Recarrega para ver a mensagem
        else:
            messagebox.showerror("Erro", msg)
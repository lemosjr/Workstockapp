import customtkinter as ctk
from app.controllers import os_controller
from tkinter import messagebox

"""
Camada View (Visão) para Solicitação de Reparo (Cliente/Inquilino).

Responsabilidade:
- Exibir um formulário simples para o cliente descrever um problema.
- Chamar o OS_Controller para criar uma nova OS com dados padrão.
"""

class SolicitacaoView(ctk.CTkToplevel):
    
    def __init__(self, master=None):
        super().__init__(master)
        
        self.title("Registrar Nova Solicitação de Reparo")
        self.geometry("450x450")
        
        self.transient(master)
        self.grab_set()
        
        self.create_widgets()

    def create_widgets(self):
        frame = ctk.CTkFrame(self)
        frame.pack(padx=20, pady=20, fill="both", expand=True)

        ctk.CTkLabel(frame, text="Nova Solicitação", 
                     font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(0, 15))

        # --- Campos do Formulário ---
        
        ctk.CTkLabel(frame, text="Endereço Completo (Apto, Casa, etc.):*").pack(anchor="w")
        self.endereco_text = ctk.CTkTextbox(frame, height=60)
        self.endereco_text.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(frame, text="Tipo de Serviço (Ex: Elétrica, Hidráulica, Pintura):*").pack(anchor="w")
        self.tipo_servico_entry = ctk.CTkEntry(frame)
        self.tipo_servico_entry.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(frame, text="Descreva o Problema/Solicitação:*").pack(anchor="w")
        self.descricao_text = ctk.CTkTextbox(frame, height=120)
        self.descricao_text.pack(fill="x", pady=(0, 10))

        # --- Botão Salvar ---
        save_button = ctk.CTkButton(frame, text="Enviar Solicitação", 
                                    command=self.enviar_solicitacao)
        save_button.pack(pady=20, side="bottom")

    def enviar_solicitacao(self):
        """
        Coleta os dados da interface e envia para o OS_Controller.
        """
        # 1. Coletar dados da View
        data = {
            "tipo_servico": self.tipo_servico_entry.get(),
            "endereco": self.endereco_text.get("1.0", "end-1c"),
            "descricao": self.descricao_text.get("1.0", "end-1c"),
            
            # --- Dados Padrão (Ocultos do Cliente) ---
            "prioridade": "baixa", # Solicitações de cliente entram como 'baixa'
            "status": "aberta", # Sempre 'aberta'
            "data_conclusao_prevista": None # A empresa define isso
        }
        
        print(f"View (Solicitacao): Coletou dados do formulário: {data}")

        # 2. Enviar dados para o Controller (reutilizamos a função de salvar OS)
        sucesso, mensagem = os_controller.salvar_os(data)
        
        # 3. Exibir resposta
        if sucesso:
            messagebox.showinfo("Sucesso", "Sua solicitação foi enviada com sucesso! Em breve a empresa entrará em contato.")
            self.destroy() # Fecha a janela
        else:
            # Mostra a mensagem de erro do controller (ex: "Endereço é obrigatório")
            messagebox.showerror("Erro de Validação", mensagem)
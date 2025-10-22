import customtkinter as ctk
from app.controllers import os_controller
from tkinter import messagebox

"""
Camada View (Visão) para Cadastro de Ordem de Serviço (OS).

Responsabilidade:
- Exibir a interface gráfica (widgets) para o usuário.
- Capturar a entrada do usuário.
- Chamar o OS_Controller quando a ação de salvar for necessária.
"""

class OSView(ctk.CTkToplevel):
    
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Criar Nova Ordem de Serviço")
        self.geometry("450x650") # Um pouco mais alta
        
        self.transient(master)
        self.grab_set()
        
        # Listas de opções (baseadas nos ENUMs do DB e Controller)
        self.prioridades_list = ["baixa", "média", "alta", "urgente"]
        self.status_list = ["aberta", "em andamento", "aguardando aprovação", "concluída", "cancelada"]
        
        self.create_widgets()

    def create_widgets(self):
        frame = ctk.CTkFrame(self)
        frame.pack(padx=20, pady=20, fill="both", expand=True)

        # --- Campos do Formulário ---
        
        ctk.CTkLabel(frame, text="Tipo de Serviço:*").pack(anchor="w")
        self.tipo_servico_entry = ctk.CTkEntry(frame)
        self.tipo_servico_entry.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(frame, text="Endereço Completo:*").pack(anchor="w")
        # Usamos Textbox para endereços longos (multi-linha)
        self.endereco_text = ctk.CTkTextbox(frame, height=80)
        self.endereco_text.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(frame, text="Descrição do Serviço/Problema:").pack(anchor="w")
        self.descricao_text = ctk.CTkTextbox(frame, height=120)
        self.descricao_text.pack(fill="x", pady=(0, 10))
        
        # --- Linha para Prioridade e Status ---
        combo_frame = ctk.CTkFrame(frame, fg_color="transparent")
        combo_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(combo_frame, text="Prioridade:").pack(side="left", padx=(0, 5))
        self.prioridade_combo = ctk.CTkComboBox(combo_frame, values=self.prioridades_list)
        self.prioridade_combo.set("baixa")
        self.prioridade_combo.pack(side="left", expand=True, fill="x", padx=(0, 10))
        
        ctk.CTkLabel(combo_frame, text="Status:").pack(side="left", padx=(0, 5))
        self.status_combo = ctk.CTkComboBox(combo_frame, values=self.status_list)
        self.status_combo.set("aberta")
        self.status_combo.pack(side="left", expand=True, fill="x")
        
        # --- Data ---
        ctk.CTkLabel(frame, text="Data Conclusão Prevista (DD/MM/AAAA):").pack(anchor="w")
        self.data_prevista_entry = ctk.CTkEntry(frame)
        self.data_prevista_entry.pack(fill="x", pady=(0, 10))

        # --- Botão Salvar ---
        save_button = ctk.CTkButton(frame, text="Salvar Ordem de Serviço", command=self.salvar)
        save_button.pack(pady=20, side="bottom")

    def salvar(self):
        """
        Coleta os dados da interface e envia para o OS_Controller.
        """
        # 1. Coletar dados da View
        # (Para .get() de Textbox, especificamos o início e fim)
        data = {
            "tipo_servico": self.tipo_servico_entry.get(),
            "endereco": self.endereco_text.get("1.0", "end-1c"), # Pega todo o texto
            "descricao": self.descricao_text.get("1.0", "end-1c"),
            "prioridade": self.prioridade_combo.get(),
            "status": self.status_combo.get(),
            "data_conclusao_prevista": self.data_prevista_entry.get() or None,
        }
        
        print(f"View (OS): Coletou dados do formulário: {data}")

        # 2. Enviar dados para o Controller
        sucesso, mensagem = os_controller.salvar_os(data)
        
        # 3. Exibir resposta
        if sucesso:
            messagebox.showinfo("Sucesso", mensagem)
            self.destroy() # Fecha a janela
        else:
            messagebox.showerror("Erro", mensagem)
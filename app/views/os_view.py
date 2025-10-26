import customtkinter as ctk
from app.controllers import os_controller
from tkinter import messagebox

"""
Camada View (Visão) para Cadastro e Edição de Ordem de Serviço (OS).
"""

class OSView(ctk.CTkToplevel):
    
    # Modificamos o __init__ para aceitar um os_id
    def __init__(self, master=None, os_id=None):
        super().__init__(master)
        
        self.transient(master)
        self.grab_set()
        
        self.os_id = os_id # Armazena o ID (None se for "Criar")
        
        # Listas de opções
        self.prioridades_list = ["baixa", "média", "alta", "urgente"]
        self.status_list = ["aberta", "em andamento", "aguardando aprovação", "concluída", "cancelada"]
        
        self.create_widgets()
        
        # --- Lógica de Edição ---
        if self.os_id:
            self.title(f"Editar Ordem de Serviço #{self.os_id}")
            self._load_data_for_edit()
        else:
            self.title("Criar Nova Ordem de Serviço")
        
        self.geometry("450x650")

    def create_widgets(self):
        frame = ctk.CTkFrame(self)
        frame.pack(padx=20, pady=20, fill="both", expand=True)

        # (O layout dos widgets é o mesmo de antes)
        
        ctk.CTkLabel(frame, text="Tipo de Serviço:*").pack(anchor="w")
        self.tipo_servico_entry = ctk.CTkEntry(frame)
        self.tipo_servico_entry.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(frame, text="Endereço Completo:*").pack(anchor="w")
        self.endereco_text = ctk.CTkTextbox(frame, height=80)
        self.endereco_text.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(frame, text="Descrição do Serviço/Problema:").pack(anchor="w")
        self.descricao_text = ctk.CTkTextbox(frame, height=120)
        self.descricao_text.pack(fill="x", pady=(0, 10))
        
        combo_frame = ctk.CTkFrame(frame, fg_color="transparent")
        combo_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(combo_frame, text="Prioridade:").pack(side="left", padx=(0, 5))
        self.prioridade_combo = ctk.CTkComboBox(combo_frame, values=self.prioridades_list)
        self.prioridade_combo.pack(side="left", expand=True, fill="x", padx=(0, 10))
        
        ctk.CTkLabel(combo_frame, text="Status:").pack(side="left", padx=(0, 5))
        self.status_combo = ctk.CTkComboBox(combo_frame, values=self.status_list)
        self.status_combo.pack(side="left", expand=True, fill="x")
        
        ctk.CTkLabel(frame, text="Data Conclusão Prevista (DD/MM/AAAA):").pack(anchor="w")
        self.data_prevista_entry = ctk.CTkEntry(frame)
        self.data_prevista_entry.pack(fill="x", pady=(0, 10))

        # O botão agora chama self.salvar (que terá a nova lógica)
        self.save_button = ctk.CTkButton(frame, text="Salvar Alterações", command=self.salvar)
        self.save_button.pack(pady=20, side="bottom")

    def _load_data_for_edit(self):
        """
        Função interna para buscar dados da OS (via Controller) e
        preencher os campos do formulário.
        """
        print(f"View (OS): Buscando dados para editar OS #{self.os_id}")
        
        sucesso, dados = os_controller.buscar_os_por_id(self.os_id)
        
        if sucesso:
            # Preenche os campos com os dados
            self.tipo_servico_entry.insert(0, dados['tipo_servico'])
            
            # Textbox (precisa deletar antes de inserir)
            self.endereco_text.delete("1.0", "end")
            self.endereco_text.insert("1.0", dados['endereco'])
            
            self.descricao_text.delete("1.0", "end")
            self.descricao_text.insert("1.0", dados['descricao'])
            
            self.prioridade_combo.set(dados['prioridade'])
            self.status_combo.set(dados['status'])
            
            self.data_prevista_entry.insert(0, dados['data_conclusao_prevista'])
        else:
            messagebox.showerror("Erro ao Carregar", dados) # 'dados' aqui é a msg de erro
            self.destroy() # Fecha a janela se não puder carregar

    def salvar(self):
        """
        Coleta os dados e decide se deve CRIAR ou ATUALIZAR.
        """
        # 1. Coletar dados da View (igual a antes)
        data = {
            "tipo_servico": self.tipo_servico_entry.get(),
            "endereco": self.endereco_text.get("1.0", "end-1c"),
            "descricao": self.descricao_text.get("1.0", "end-1c"),
            "prioridade": self.prioridade_combo.get(),
            "status": self.status_combo.get(),
            "data_conclusao_prevista": self.data_prevista_entry.get() or None,
        }
        
        print(f"View (OS): Salvando. Modo Edição (ID: {self.os_id})")

        # 2. Decidir qual função do Controller chamar
        if self.os_id:
            # --- MODO UPDATE ---
            sucesso, mensagem = os_controller.atualizar_os(self.os_id, data)
        else:
            # --- MODO CREATE ---
            sucesso, mensagem = os_controller.salvar_os(data)
        
        # 3. Exibir resposta
        if sucesso:
            messagebox.showinfo("Sucesso", mensagem)
            self.destroy() # Fecha a janela
        else:
            messagebox.showerror("Erro", mensagem)
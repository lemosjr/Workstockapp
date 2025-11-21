import customtkinter as ctk
from app.controllers import os_controller
from tkinter import messagebox

# --- PALETA DE CORES (Mesma da MainView) ---
COLOR_PRIMARY = "#264653"
COLOR_SECONDARY = "#2A5159"
COLOR_ACCENT = "#F2B263"
COLOR_ACCENT_HOVER = "#D9A059"
COLOR_TEXT_DARK = "#264653"

class OSView(ctk.CTkToplevel):
    
    def __init__(self, master=None, os_id=None):
        super().__init__(master)
        
        self.transient(master)
        self.grab_set()
        
        self.os_id = os_id
        
        self.prioridades_list = ["baixa", "média", "alta", "urgente"]
        self.status_list = ["aberta", "em andamento", "aguardando aprovação", "concluída", "cancelada"]
        
        # Configurações da Janela
        title_text = f"Editar OS #{self.os_id}" if self.os_id else "Criar Nova Ordem de Serviço"
        self.title(title_text)
        self.geometry("500x700")
        
        self.create_widgets(title_text)
        
        if self.os_id:
            self._load_data_for_edit()

    def create_widgets(self, title_text):
        # --- Cabeçalho ---
        header_frame = ctk.CTkFrame(self, height=60, corner_radius=0, fg_color=COLOR_PRIMARY)
        header_frame.pack(fill="x", side="top")
        
        ctk.CTkLabel(header_frame, text=title_text, 
                     font=("Roboto Medium", 20), text_color="white").pack(pady=15)

        # --- Corpo do Formulário ---
        # Usamos um ScrollableFrame caso a tela seja pequena
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Campos
        self._add_label("Tipo de Serviço:*")
        self.tipo_servico_entry = ctk.CTkEntry(self.scroll_frame, height=35)
        self.tipo_servico_entry.pack(fill="x", pady=(0, 15))

        self._add_label("Endereço Completo:*")
        self.endereco_text = ctk.CTkTextbox(self.scroll_frame, height=80)
        self.endereco_text.pack(fill="x", pady=(0, 15))

        self._add_label("Descrição do Serviço/Problema:")
        self.descricao_text = ctk.CTkTextbox(self.scroll_frame, height=100)
        self.descricao_text.pack(fill="x", pady=(0, 15))
        
        # Grid para Prioridade e Status
        grid_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        grid_frame.pack(fill="x", pady=(0, 15))
        
        # Prioridade
        ctk.CTkLabel(grid_frame, text="Prioridade:", font=("Roboto", 12)).pack(anchor="w")
        self.prioridade_combo = ctk.CTkComboBox(grid_frame, values=self.prioridades_list, 
                                                button_color=COLOR_PRIMARY)
        self.prioridade_combo.pack(fill="x", pady=(5, 10))
        
        # Status
        ctk.CTkLabel(grid_frame, text="Status:", font=("Roboto", 12)).pack(anchor="w")
        self.status_combo = ctk.CTkComboBox(grid_frame, values=self.status_list,
                                            button_color=COLOR_PRIMARY)
        self.status_combo.pack(fill="x", pady=(5, 0))
        
        self._add_label("Data Previsão (DD/MM/AAAA):")
        self.data_prevista_entry = ctk.CTkEntry(self.scroll_frame, height=35)
        self.data_prevista_entry.pack(fill="x", pady=(0, 10))

        # --- Botão Salvar (Footer) ---
        # Fica fixo na parte de baixo, fora do scroll
        footer_frame = ctk.CTkFrame(self, height=70, fg_color="transparent")
        footer_frame.pack(fill="x", side="bottom", padx=20, pady=20)

        self.save_button = ctk.CTkButton(
            footer_frame, 
            text="SALVAR DADOS",
            height=45,
            font=("Roboto Medium", 14),
            fg_color=COLOR_ACCENT, 
            hover_color=COLOR_ACCENT_HOVER, 
            text_color=COLOR_TEXT_DARK,
            command=self.salvar
        )
        self.save_button.pack(fill="x")

    def _add_label(self, text):
        ctk.CTkLabel(self.scroll_frame, text=text, 
                     font=("Roboto", 12, "bold"), text_color="gray").pack(anchor="w", pady=(5, 2))

    def _load_data_for_edit(self):
        sucesso, dados = os_controller.buscar_os_por_id(self.os_id)
        if sucesso:
            self.tipo_servico_entry.insert(0, dados['tipo_servico'])
            self.endereco_text.insert("1.0", dados['endereco'])
            self.descricao_text.insert("1.0", dados['descricao'])
            self.prioridade_combo.set(dados['prioridade'])
            self.status_combo.set(dados['status'])
            self.data_prevista_entry.insert(0, dados['data_conclusao_prevista'])
        else:
            messagebox.showerror("Erro", dados)
            self.destroy()

    def salvar(self):
        data = {
            "tipo_servico": self.tipo_servico_entry.get(),
            "endereco": self.endereco_text.get("1.0", "end-1c"),
            "descricao": self.descricao_text.get("1.0", "end-1c"),
            "prioridade": self.prioridade_combo.get(),
            "status": self.status_combo.get(),
            "data_conclusao_prevista": self.data_prevista_entry.get() or None,
        }
        
        if self.os_id:
            sucesso, mensagem = os_controller.atualizar_os(self.os_id, data)
        else:
            sucesso, mensagem = os_controller.salvar_os(data)
        
        if sucesso:
            messagebox.showinfo("Sucesso", mensagem)
            self.destroy()
        else:
            messagebox.showerror("Erro", mensagem)
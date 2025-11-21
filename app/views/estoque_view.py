import customtkinter as ctk
from app.controllers import estoque_controller
from tkinter import messagebox

# --- PALETA DE CORES ---
COLOR_PRIMARY = "#264653"
COLOR_ACCENT = "#F2B263"
COLOR_ACCENT_HOVER = "#D9A059"
COLOR_TEXT_DARK = "#264653"

class EstoqueView(ctk.CTkToplevel):
    
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Cadastrar Novo Material")
        self.geometry("450x600")
        self.transient(master)
        self.grab_set()
        
        self.create_widgets()

    def create_widgets(self):
        # --- Cabeçalho ---
        header_frame = ctk.CTkFrame(self, height=60, corner_radius=0, fg_color=COLOR_PRIMARY)
        header_frame.pack(fill="x", side="top")
        
        ctk.CTkLabel(header_frame, text="Novo Material", 
                     font=("Roboto Medium", 20), text_color="white").pack(pady=15)

        # --- Corpo (Scrollable) ---
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True, padx=20, pady=20)

        self._add_field("Nome do Material:*", "nome_entry")
        self._add_field("SKU (Código):*", "sku_entry")
        self._add_field("Unidade de Medida (ex: un, kg):", "unidade_entry")
        
        # Preço e Estoque lado a lado
        row1 = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        row1.pack(fill="x", pady=5)
        
        self._add_field_grid(row1, "Preço Custo (R$):", "preco_entry", 0)
        self._add_field_grid(row1, "Estoque Inicial:", "estoque_entry", 1)

        self._add_field("Estoque Mínimo (Alerta):", "estoque_min_entry")
        self._add_field("Fornecedor Preferencial:", "fornecedor_entry")
        self._add_field("Localização no Estoque:", "localizacao_entry")

        # --- Botão Salvar ---
        self.save_button = ctk.CTkButton(
            self, 
            text="CADASTRAR MATERIAL",
            height=45,
            font=("Roboto Medium", 14),
            fg_color=COLOR_ACCENT, 
            hover_color=COLOR_ACCENT_HOVER, 
            text_color=COLOR_TEXT_DARK,
            command=self.salvar
        )
        self.save_button.pack(fill="x", padx=20, pady=20, side="bottom")

    def _add_field(self, label_text, attr_name):
        ctk.CTkLabel(self.scroll_frame, text=label_text, 
                     font=("Roboto", 12, "bold"), text_color="gray").pack(anchor="w", pady=(5, 2))
        entry = ctk.CTkEntry(self.scroll_frame, height=35)
        entry.pack(fill="x", pady=(0, 10))
        setattr(self, attr_name, entry) # Cria self.nome_entry, etc.

    def _add_field_grid(self, parent, label_text, attr_name, col):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(side="left", fill="x", expand=True, padx=(0 if col==0 else 10, 0))
        
        ctk.CTkLabel(frame, text=label_text, 
                     font=("Roboto", 12, "bold"), text_color="gray").pack(anchor="w", pady=(0, 2))
        entry = ctk.CTkEntry(frame, height=35)
        entry.pack(fill="x")
        setattr(self, attr_name, entry)

    def salvar(self):
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
        
        sucesso, mensagem = estoque_controller.salvar_material(data)
        
        if sucesso:
            messagebox.showinfo("Sucesso", mensagem)
            self.destroy()
        else:
            messagebox.showerror("Erro", mensagem)
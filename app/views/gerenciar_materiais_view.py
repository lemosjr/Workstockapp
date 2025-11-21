import customtkinter as ctk
from tkinter import ttk, messagebox
from app.controllers import os_controller, estoque_controller

# --- PALETA DE CORES ---
COLOR_PRIMARY = "#264653"
COLOR_SECONDARY = "#2A5159"
COLOR_ACCENT = "#F2B263"
COLOR_ACCENT_HOVER = "#D9A059"
COLOR_DANGER = "#BF4124"
COLOR_DANGER_HOVER = "#A6391F"
COLOR_TEXT_DARK = "#264653"
COLOR_BG_LIGHT = "#F2F2F2"

class GerenciarMateriaisView(ctk.CTkToplevel):
    
    def __init__(self, master, os_id):
        super().__init__(master)
        
        if not os_id:
            messagebox.showerror("Erro", "ID da OS inválido.")
            self.destroy()
            return
            
        self.os_id = os_id
        self.title(f"Gerenciar Materiais - OS #{self.os_id}")
        self.geometry("950x600")
        
        self.transient(master)
        self.grab_set()
        
        self.inventory_map = {}
        
        self._setup_styles()
        self.create_widgets()
        
        self._load_inventory_list()
        self._load_linked_materials()
        self._load_orcamento_data()

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use("default")
        
        style.configure("Treeview", 
                        background="#2b2b2b", 
                        foreground=COLOR_BG_LIGHT, 
                        fieldbackground="#2b2b2b", 
                        rowheight=25, 
                        borderwidth=0)
        
        style.map('Treeview', background=[('selected', COLOR_ACCENT)], foreground=[('selected', COLOR_TEXT_DARK)])
        
        style.configure("Treeview.Heading", 
                        background=COLOR_PRIMARY, 
                        foreground=COLOR_BG_LIGHT, 
                        font=("Roboto", 10, "bold"), 
                        relief="flat")
        
        style.map("Treeview.Heading", background=[('active', COLOR_SECONDARY)])

    def create_widgets(self):
        # --- Cabeçalho ---
        header_frame = ctk.CTkFrame(self, height=60, corner_radius=0, fg_color=COLOR_PRIMARY)
        header_frame.pack(fill="x", side="top")
        
        ctk.CTkLabel(header_frame, text=f"Gerenciar Materiais e Orçamento - OS #{self.os_id}", 
                     font=("Roboto Medium", 20), text_color="white").pack(pady=15)

        # --- Container Principal ---
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=20, pady=20)

        # --- ESQUERDA: Tabela de Materiais ---
        left_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 20))
        
        ctk.CTkLabel(left_frame, text="Materiais Vinculados", 
                     font=("Roboto", 14, "bold"), text_color="gray").pack(anchor="w", pady=(0, 5))

        self.create_linked_table(left_frame)
        
        self.remove_button = ctk.CTkButton(
            left_frame, text="Remover Selecionado", 
            command=self._on_remove_material,
            fg_color="transparent", border_width=1, border_color=COLOR_DANGER,
            text_color=COLOR_DANGER, hover_color=COLOR_PRIMARY
        )
        self.remove_button.pack(pady=10, anchor="e")
        
        # --- DIREITA: Painel de Ações ---
        right_frame = ctk.CTkFrame(main_container, width=320, corner_radius=15, fg_color=COLOR_SECONDARY)
        right_frame.pack(side="right", fill="y")
        right_frame.pack_propagate(False)

        # Seção: Adicionar Material
        ctk.CTkLabel(right_frame, text="ADICIONAR DO ESTOQUE", 
                     font=("Roboto", 12, "bold"), text_color="#AABEC9").pack(pady=(20, 10))
        
        self.material_combo = ctk.CTkComboBox(right_frame, values=["Carregando..."], width=280)
        self.material_combo.pack(pady=(0, 10))
        
        self.quantidade_entry = ctk.CTkEntry(right_frame, width=280, placeholder_text="Quantidade")
        self.quantidade_entry.pack(pady=(0, 15))
        
        self.add_button = ctk.CTkButton(
            right_frame, text="Adicionar à Lista", 
            command=self._on_add_material,
            fg_color=COLOR_ACCENT, hover_color=COLOR_ACCENT_HOVER, text_color=COLOR_TEXT_DARK
        )
        self.add_button.pack(pady=(0, 20))

        # Divisor
        ctk.CTkFrame(right_frame, height=2, fg_color=COLOR_PRIMARY).pack(fill="x", padx=20, pady=10)
        
        # Seção: Orçamento
        ctk.CTkLabel(right_frame, text="RESUMO FINANCEIRO", 
                     font=("Roboto", 12, "bold"), text_color="#AABEC9").pack(pady=(10, 10))
        
        # Grid para valores
        vals_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        vals_frame.pack(fill="x", padx=20)
        
        ctk.CTkLabel(vals_frame, text="Materiais:", text_color="white").grid(row=0, column=0, sticky="w", pady=2)
        self.custo_materiais_label = ctk.CTkLabel(vals_frame, text="R$ 0.00", font=("Roboto", 14, "bold"), text_color="white")
        self.custo_materiais_label.grid(row=0, column=1, sticky="e", padx=10)
        
        ctk.CTkLabel(vals_frame, text="Mão de Obra:", text_color="white").grid(row=1, column=0, sticky="w", pady=15)
        self.mao_de_obra_entry = ctk.CTkEntry(vals_frame, width=100, height=25)
        self.mao_de_obra_entry.grid(row=1, column=1, sticky="e", padx=10)
        
        ctk.CTkFrame(right_frame, height=1, fg_color="gray").pack(fill="x", padx=40, pady=10)

        # Total
        total_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        total_frame.pack(fill="x", padx=20)
        ctk.CTkLabel(total_frame, text="TOTAL:", font=("Roboto", 16, "bold"), text_color=COLOR_ACCENT).pack(side="left")
        self.custo_total_label = ctk.CTkLabel(total_frame, text="R$ 0.00", font=("Roboto", 20, "bold"), text_color=COLOR_ACCENT)
        self.custo_total_label.pack(side="right", padx=10)
        
        # Botão Salvar
        self.save_orcamento_button = ctk.CTkButton(
            right_frame, text="Salvar Orçamento",
            command=self._on_save_orcamento,
            fg_color=COLOR_PRIMARY, hover_color="#1D343E", border_width=1, border_color=COLOR_ACCENT, text_color="white"
        )
        self.save_orcamento_button.pack(side="bottom", pady=30)

    def create_linked_table(self, parent_frame):
        columns = ("os_material_id", "material_id", "nome", "sku", "qtd", "custo_unit")
        self.linked_tree = ttk.Treeview(parent_frame, columns=columns, show="headings")
        
        self.linked_tree.heading("os_material_id", text="ID"); self.linked_tree.heading("material_id", text="Mat ID")
        self.linked_tree.heading("nome", text="Material"); self.linked_tree.heading("sku", text="SKU")
        self.linked_tree.heading("qtd", text="Qtd"); self.linked_tree.heading("custo_unit", text="Custo Un.")
        
        self.linked_tree.column("os_material_id", width=40, anchor="center"); self.linked_tree.column("material_id", width=0, stretch="no")
        self.linked_tree.column("nome", width=180); self.linked_tree.column("sku", width=100)
        self.linked_tree.column("qtd", width=50, anchor="center"); self.linked_tree.column("custo_unit", width=80, anchor="e")
        
        self.linked_tree.pack(fill="both", expand=True)

    # --- LÓGICA (Inalterada, apenas colada para manter o arquivo funcional) ---
    
    def _load_inventory_list(self):
        sucesso, materiais = estoque_controller.listar_materiais()
        if not sucesso: return
        combo_values = []
        self.inventory_map = {} 
        for m in materiais:
            display_name = f"{m['nome']} (Estoque: {m['estoque_atual']})"
            combo_values.append(display_name)
            self.inventory_map[display_name] = m['id']
        self.material_combo.configure(values=combo_values)
        if combo_values: self.material_combo.set(combo_values[0])
        else: self.material_combo.set("")

    def _load_linked_materials(self):
        for item in self.linked_tree.get_children(): self.linked_tree.delete(item)
        sucesso, dados = os_controller.listar_materiais_da_os(self.os_id)
        if sucesso:
            for item in dados:
                valores = (item['os_material_id'], item['material_id'], item['material_nome'], item['sku'], item['quantidade'], f"{item['preco_custo_na_data']:.2f}")
                self.linked_tree.insert("", "end", values=valores)

    def _on_add_material(self):
        selected_name = self.material_combo.get()
        quantidade = self.quantidade_entry.get()
        if not selected_name or not self.inventory_map or selected_name == "Carregando...":
            messagebox.showwarning("Aviso", "Nenhum material selecionado.")
            return
        try: material_id = self.inventory_map[selected_name]
        except KeyError: return
        sucesso, msg = os_controller.vincular_material_os(self.os_id, material_id, quantidade)
        if sucesso:
            messagebox.showinfo("Sucesso", msg)
            self._load_inventory_list(); self._load_linked_materials(); self._load_orcamento_data()
            self.quantidade_entry.delete(0, 'end')
        else:
            messagebox.showerror("Erro", msg); self._load_inventory_list()

    def _on_remove_material(self):
        selected_item = self.linked_tree.focus()
        if not selected_item: return
        item_values = self.linked_tree.item(selected_item, "values")
        try:
            os_material_id = int(item_values[0]); material_id = int(item_values[1])
            material_nome = item_values[2]; quantidade_removida = int(item_values[4])
        except: return
        if not messagebox.askyesno("Confirmar", f"Remover '{material_nome}'? O estoque será estornado."): return
        sucesso, msg = os_controller.desvincular_material_os(os_material_id, material_id, quantidade_removida)
        if sucesso:
            messagebox.showinfo("Sucesso", msg)
            self._load_inventory_list(); self._load_linked_materials(); self._load_orcamento_data()
        else: messagebox.showerror("Erro", msg)

    def _load_orcamento_data(self):
        sucesso, data = os_controller.get_orcamento_os(self.os_id)
        if sucesso:
            self.custo_materiais_label.configure(text=f"R$ {data.get('materiais', 0.0):.2f}")
            self.custo_total_label.configure(text=f"R$ {data.get('total', 0.0):.2f}")
            self.mao_de_obra_entry.delete(0, 'end')
            self.mao_de_obra_entry.insert(0, f"{data.get('mao_de_obra', 0.0):.2f}")

    def _on_save_orcamento(self):
        mao_de_obra_str = self.mao_de_obra_entry.get()
        sucesso, msg = os_controller.recalcular_e_salvar_orcamento_os(self.os_id, mao_de_obra_str)
        if sucesso:
            messagebox.showinfo("Sucesso", msg)
            self._load_orcamento_data()
        else: messagebox.showerror("Erro", msg)
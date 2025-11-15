import customtkinter as ctk
from tkinter import ttk, messagebox
from app.controllers import os_controller, estoque_controller

"""
Camada View (Visão) para Gerenciamento de Materiais de uma OS.

Responsabilidade:
- Exibir os materiais já vinculados a uma OS.
- Permitir adicionar novos materiais do estoque (dando baixa).
- Permitir remover materiais da OS (estornando estoque).
"""

class GerenciarMateriaisView(ctk.CTkToplevel):
    
    def __init__(self, master, os_id):
        super().__init__(master)
        
        if not os_id:
            messagebox.showerror("Erro", "ID da OS inválido.")
            self.destroy()
            return
            
        self.os_id = os_id
        self.title(f"Gerenciar Materiais da OS #{self.os_id}")
        self.geometry("1000x800")
        
        self.transient(master)
        self.grab_set()
        
        # Mapa para o ComboBox (para ligar "Nome" ao ID)
        self.inventory_map = {}
        
        self._setup_styles() # Configura o estilo do Treeview
        self.create_widgets()
        
        # Carrega os dados iniciais
        self._load_inventory_list() # Carrega o ComboBox de estoque
        self._load_linked_materials() # Carrega a tabela de materiais da OS
        self._load_orcamento_data()

    def _setup_styles(self):
        """ Configura o estilo do Treeview para o tema escuro. """
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background="#2b2b2b", foreground="#dce4ee", fieldbackground="#343638", rowheight=25, borderwidth=0)
        style.map('Treeview', background=[('selected', '#3471CD')])
        style.configure("Treeview.Heading", background="#565B5E", foreground="#dce4ee", font=("Arial", 10, "bold"), relief="flat")
        style.map("Treeview.Heading", background=[('active', '#343638')])

    def create_widgets(self):
        # --- Frame Esquerdo (Materiais VINCULADOS) ---
        left_frame = ctk.CTkFrame(self)
        left_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(left_frame, text="Materiais Vinculados a esta OS", font=("Arial", 16)).pack(pady=5)

        self.create_linked_table(left_frame)
        
        self.remove_button = ctk.CTkButton(
            left_frame, text="Remover Material Selecionado", 
            command=self._on_remove_material,
            fg_color="#DB3E3E", hover_color="#B73030"
        )
        self.remove_button.pack(pady=10)
        
        # --- Frame Direito (Adicionar + ORÇAMENTO) ---
        right_frame = ctk.CTkFrame(self, width=350)
        right_frame.pack(side="right", fill="y", padx=10, pady=10)
        right_frame.pack_propagate(False) 

        ctk.CTkLabel(right_frame, text="Adicionar do Estoque", font=("Arial", 16)).pack(pady=5)
        
        ctk.CTkLabel(right_frame, text="Material:").pack(anchor="w", padx=10)
        self.material_combo = ctk.CTkComboBox(right_frame, values=["Carregando..."])
        self.material_combo.pack(fill="x", padx=10, pady=(0, 10))
        
        ctk.CTkLabel(right_frame, text="Quantidade:").pack(anchor="w", padx=10)
        self.quantidade_entry = ctk.CTkEntry(right_frame, width=100)
        self.quantidade_entry.pack(anchor="w", padx=10, pady=(0, 20))
        
        self.add_button = ctk.CTkButton(
            right_frame, text="Adicionar Material à OS", 
            command=self._on_add_material
        )
        self.add_button.pack(pady=10)

        # --- SEPARAÇÃO E NOVA SEÇÃO DE ORÇAMENTO ---
        ctk.CTkFrame(right_frame, height=2, fg_color="gray").pack(fill="x", padx=10, pady=(15, 10))
        
        ctk.CTkLabel(right_frame, text="Resumo do Orçamento", font=("Arial", 16)).pack(pady=5)
        
        # Custo de Materiais (Calculado)
        ctk.CTkLabel(right_frame, text="Custo Materiais (R$):").pack(anchor="w", padx=10)
        self.custo_materiais_label = ctk.CTkLabel(right_frame, text="R$ 0.00", font=("Arial", 14, "bold"))
        self.custo_materiais_label.pack(anchor="w", padx=10, pady=(0, 10))
        
        # Custo de Mão de Obra (Editável)
        ctk.CTkLabel(right_frame, text="Mão de Obra (R$):").pack(anchor="w", padx=10)
        self.mao_de_obra_entry = ctk.CTkEntry(right_frame)
        self.mao_de_obra_entry.pack(fill="x", padx=10, pady=(0, 10))
        
        # Custo Total (Calculado)
        ctk.CTkLabel(right_frame, text="CUSTO TOTAL (R$):").pack(anchor="w", padx=10)
        self.custo_total_label = ctk.CTkLabel(right_frame, text="R$ 0.00", font=("Arial", 16, "bold"), text_color="#4CAF50") # Cor verde
        self.custo_total_label.pack(anchor="w", padx=10, pady=(0, 20))
        
        # Botão Salvar Orçamento
        self.save_orcamento_button = ctk.CTkButton(
            right_frame, text="Salvar Orçamento",
            command=self._on_save_orcamento
        )
        self.save_orcamento_button.pack(pady=20, side="bottom")

    def create_linked_table(self, parent_frame):
        """ Cria a tabela (Treeview) para exibir os materiais vinculados. """
        columns = ("os_material_id", "material_id", "nome", "sku", "qtd", "custo_unit")
        
        self.linked_tree = ttk.Treeview(parent_frame, columns=columns, show="headings")
        
        self.linked_tree.heading("os_material_id", text="ID Vínculo")
        self.linked_tree.heading("material_id", text="ID Mat.")
        self.linked_tree.heading("nome", text="Nome")
        self.linked_tree.heading("sku", text="SKU")
        self.linked_tree.heading("qtd", text="Qtd.")
        self.linked_tree.heading("custo_unit", text="Custo (Un.)")
        
        self.linked_tree.column("os_material_id", width=70, anchor="center")
        self.linked_tree.column("material_id", width=50, anchor="center")
        self.linked_tree.column("nome", width=150)
        self.linked_tree.column("sku", width=80)
        self.linked_tree.column("qtd", width=50, anchor="center")
        self.linked_tree.column("custo_unit", width=80, anchor="e")
        
        self.linked_tree.pack(fill="both", expand=True, padx=5, pady=5)

    def _load_orcamento_data(self):
        """
        Busca os dados de orçamento (salvos) e atualiza os campos.
        """
        print(f"View (Mat): Carregando dados do orçamento da OS {self.os_id}")
        sucesso, data = os_controller.get_orcamento_os(self.os_id)
        
        if sucesso:
            # Pega os valores do banco
            custo_materiais = data.get('materiais', 0.0)
            custo_mo = data.get('mao_de_obra', 0.0)
            custo_total = data.get('total', 0.0)
            
            # Atualiza os Labels
            self.custo_materiais_label.configure(text=f"R$ {custo_materiais:.2f}")
            self.custo_total_label.configure(text=f"R$ {custo_total:.2f}")
            
            # Atualiza o Entry (só limpamos e inserimos)
            self.mao_de_obra_entry.delete(0, 'end')
            self.mao_de_obra_entry.insert(0, f"{custo_mo:.2f}")
            
        else:
            messagebox.showerror("Erro", "Não foi possível carregar os dados do orçamento.")

    def _on_save_orcamento(self):
        """
        Chamado pelo botão "Salvar Orçamento".
        Pega a Mão de Obra e manda o Controller recalcular tudo.
        """
        mao_de_obra_str = self.mao_de_obra_entry.get()
        
        print(f"View (Mat): Solicitando recalcular e salvar orçamento da OS {self.os_id} com M.O. = {mao_de_obra_str}")
        
        # O Controller fará todo o trabalho de cálculo
        sucesso, msg = os_controller.recalcular_e_salvar_orcamento_os(
            self.os_id,
            mao_de_obra_str
        )
        
        if sucesso:
            messagebox.showinfo("Sucesso", msg)
            # Recarrega os dados para mostrar os valores atualizados
            self._load_orcamento_data()
        else:
            messagebox.showerror("Erro ao Salvar", msg)

    def _load_inventory_list(self):
        """ Busca o estoque completo para popular o ComboBox. """
        print("View (Mat): Carregando lista do estoque...")
        sucesso, materiais = estoque_controller.listar_materiais()
        if not sucesso:
            messagebox.showerror("Erro", "Não foi possível carregar o estoque.")
            return

        combo_values = []
        self.inventory_map = {} # Limpa o mapa

        for m in materiais:
            # Texto amigável para o ComboBox
            display_name = f"{m['nome']} (Estoque: {m['estoque_atual']})"
            combo_values.append(display_name)
            
            # Mapeia o texto amigável de volta para o ID do material
            self.inventory_map[display_name] = m['id']
            
        self.material_combo.configure(values=combo_values)
        if combo_values:
            self.material_combo.set(combo_values[0]) # Seleciona o primeiro

    def _load_linked_materials(self):
        """ Busca os materiais já vinculados a esta OS. """
        # Limpa a tabela
        for item in self.linked_tree.get_children():
            self.linked_tree.delete(item)
            
        sucesso, dados = os_controller.listar_materiais_da_os(self.os_id)
        
        if sucesso:
            for item in dados:
                valores = (
                    item['os_material_id'],
                    item['material_id'],
                    item['material_nome'],
                    item['sku'],
                    item['quantidade'],
                    f"{item['preco_custo_na_data']:.2f}"
                )
                self.linked_tree.insert("", "end", values=valores)
        else:
            messagebox.showerror("Erro", "Não foi possível carregar os materiais desta OS.")

    def _on_add_material(self):
        """ Chamado pelo botão 'Adicionar Material'. """
        
        # 1. Obter os dados do formulário
        selected_name = self.material_combo.get()
        quantidade = self.quantidade_entry.get()
        
        # 2. Validar
        if not selected_name or not self.inventory_map:
            messagebox.showwarning("Aviso", "Nenhum material selecionado.")
            return
            
        try:
            # 3. Usar o mapa para encontrar o ID
            material_id = self.inventory_map[selected_name]
        except KeyError:
            messagebox.showwarning("Aviso", "Material inválido ou não encontrado.")
            return
            
        print(f"View (Mat): Solicitando ao Controller para vincular OS {self.os_id} <-> Mat {material_id} (Qtd: {quantidade})")

        # 4. Chamar o Controller
        sucesso, msg = os_controller.vincular_material_os(self.os_id, material_id, quantidade)
        
        if sucesso:
            messagebox.showinfo("Sucesso", msg)
            # 5. Recarregar TUDO para mostrar as mudanças
            self._load_inventory_list() # Recarrega o ComboBox (para estoque atualizado)
            self._load_linked_materials() # Recarrega a Tabela (para item novo)
            self._load_orcamento_data() # Recarrega o orçamento (custo atualizado)
            self.quantidade_entry.delete(0, 'end') # Limpa o campo
        else:
            messagebox.showerror("Erro ao Adicionar", msg)

    def _on_remove_material(self):
        """ Chamado pelo botão 'Remover Material Selecionado'. """
        
        # 1. Obter o item selecionado da tabela
        selected_item = self.linked_tree.focus()
        if not selected_item:
            messagebox.showwarning("Aviso", "Selecione um material da lista para remover.")
            return

        # 2. Obter os valores (precisamos do ID e da quantidade para estornar)
        item_values = self.linked_tree.item(selected_item, "values")
        
        try:
            os_material_id = int(item_values[0]) # ID do VÍNCULO (da tabela os_materiais)
            material_id = int(item_values[1])    # ID do MATERIAL (para estornar)
            material_nome = item_values[2]
            quantidade_removida = int(item_values[4])
        except (IndexError, TypeError, ValueError):
            messagebox.showerror("Erro", "Não foi possível ler os dados do item selecionado.")
            return

        # 3. Pedir Confirmação
        if not messagebox.askyesno("Confirmar Remoção", 
                                   f"Deseja remover '{material_nome}' (Qtd: {quantidade_removida}) desta OS?\n\n"
                                   f"O estoque será ESTORNADO (devolvido)."):
            return

        # 4. Chamar o Controller
        print(f"View (Mat): Solicitando ao Controller desvincular ID {os_material_id} (Estornar Qtd {quantidade_removida} para Mat {material_id})")
        
        sucesso, msg = os_controller.desvincular_material_os(os_material_id, material_id, quantidade_removida)
        
        if sucesso:
            messagebox.showinfo("Sucesso", msg)
            # 5. Recarregar TUDO
            self._load_inventory_list()
            self._load_linked_materials()
            self._load_orcamento_data()
        else:
            messagebox.showerror("Erro ao Remover", msg)
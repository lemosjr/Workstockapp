from app.models import estoque_model
import decimal # Usaremos para validar o preço

"""
Camada Controller (Controlador) para Estoque.
Atualizado com CRUD completo e refatoração da validação.

Responsabilidade:
- Orquestrar a lógica de negócio.
- Fazer a ponte entre a View e o Model.
- Recebe dados da View, valida-os (lógica de negócio) e envia para o Model.
- Solicita dados ao Model e os envia para a View.
"""

def _validar_e_formatar_dados_material(data):
    """
    Função auxiliar PRIVADA para validar e formatar dados do material.
    Usada por 'salvar_material' e 'atualizar_material'.
    Retorna (True, dados_formatados) ou (False, mensagem_erro).
    """
    
    # --- 1. Lógica de Negócio e Validação ---
    
    if not data.get('nome') or len(data['nome'].strip()) == 0:
        print("Controller Error: O nome é obrigatório.")
        return (False, "O nome do material é obrigatório.")

    if not data.get('sku') or len(data['sku'].strip()) == 0:
        print("Controller Error: O SKU é obrigatório.")
        return (False, "O SKU do material é obrigatório.")
        
    try:
        preco = data.get('preco_custo')
        data['preco_custo'] = decimal.Decimal(preco if preco else 0.0)
        
        estoque = data.get('estoque_atual')
        data['estoque_atual'] = int(estoque if estoque else 0)
        
        estoque_min = data.get('estoque_minimo')
        data['estoque_minimo'] = int(estoque_min if estoque_min else 0)
        
    except (decimal.InvalidOperation, ValueError) as e:
        print(f"Controller Error: Dados numéricos inválidos. {e}")
        return (False, "Erro: Preço ou Estoque devem ser números válidos.")
        
    # Garantir que campos opcionais sejam strings vazias se não forem fornecidos
    data['unidade_medida'] = data.get('unidade_medida', '')
    data['fornecedor'] = data.get('fornecedor', '')
    data['localizacao'] = data.get('localizacao', '')
    
    # Se todas as validações passaram, retorna os dados formatados
    return (True, data)


# --- FUNÇÃO ATUALIZADA (Refatorada) ---
def salvar_material(data):
    """
    Controlador para salvar um novo material.
    'data' é um dicionário vindo da View.
    """
    
    # --- 1. Validação ---
    sucesso_validacao, dados_ou_erro = _validar_e_formatar_dados_material(data)
    
    if not sucesso_validacao:
        return (False, dados_ou_erro) # Retorna a msg de erro
    
    dados_formatados = dados_ou_erro

    # --- 2. Chamada ao Model ---
    print(f"Controller: Dados validados. Enviando para o Model (Create): {dados_formatados}")
    novo_id = estoque_model.create_material(dados_formatados)
    
    # --- 3. Resposta para a View ---
    if novo_id:
        return (True, f"Material '{dados_formatados['nome']}' salvo com sucesso! (ID: {novo_id})")
    else:
        # O Model já imprimiu o erro específico (ex: "UNIQUE constraint failed")
        return (False, "Erro ao salvar o material no banco de dados. (SKU duplicado?)")


# --- FUNÇÃO NOVA ---
def atualizar_material(material_id, data):
    """
    Controlador para ATUALIZAR um material existente.
    """
    
    # --- 1. Validação (Reutilizando a função) ---
    sucesso_validacao, dados_ou_erro = _validar_e_formatar_dados_material(data)
    
    if not sucesso_validacao:
        return (False, dados_ou_erro) # Retorna a msg de erro
    
    dados_formatados = dados_ou_erro

    # --- 2. Chamada ao Model ---
    print(f"Controller: Dados validados. Enviando para o Model (Update): {dados_formatados}")
    sucesso_update = estoque_model.update_material(material_id, dados_formatados)
    
    # --- 3. Resposta para a View ---
    if sucesso_update:
        return (True, f"Material '{dados_formatados['nome']}' (ID: {material_id}) atualizado com sucesso!")
    else:
        return (False, f"Erro ao atualizar o material ID {material_id}. (SKU duplicado?)")


# --- FUNÇÃO NOVA ---
def buscar_material_por_id(material_id):
    """
    Controlador para buscar os dados de UM material.
    Usado para preencher o formulário de edição.
    """
    print(f"Controller: Buscando dados do material ID #{material_id}.")
    try:
        material_data = estoque_model.get_material_by_id(material_id)
        
        if material_data:
            # Converte o DictRow para um dict padrão
            dados_formatados = dict(material_data)
            
            # Formata os dados de volta para a View (que só entende strings)
            dados_formatados['preco_custo'] = str(dados_formatados.get('preco_custo', '0.00'))
            dados_formatados['estoque_atual'] = str(dados_formatados.get('estoque_atual', '0'))
            dados_formatados['estoque_minimo'] = str(dados_formatados.get('estoque_minimo', '0'))
            
            # Garante que campos nulos sejam strings vazias
            dados_formatados['unidade_medida'] = dados_formatados.get('unidade_medida') or ""
            dados_formatados['fornecedor_preferencial'] = dados_formatados.get('fornecedor_preferencial') or ""
            dados_formatados['localizacao'] = dados_formatados.get('localizacao') or ""
            
            # Renomeia a chave para bater com o que a View espera
            dados_formatados['fornecedor'] = dados_formatados.pop('fornecedor_preferencial', '')

            return (True, dados_formatados)
        else:
            return (False, f"Nenhum material encontrado com o ID {material_id}.")
            
    except Exception as e:
        print(f"Controller Error: Erro ao buscar material por ID. {e}")
        return (False, "Erro ao buscar dados do material. Verifique o console.")


# --- FUNÇÃO NOVA ---
def deletar_material(material_id):
    """
    Controlador para deletar um material.
    """
    if not material_id:
        return (False, "Nenhum material selecionado para deletar.")
        
    print(f"Controller: Solicitando exclusão do material ID #{material_id}.")
    
    try:
        sucesso = estoque_model.delete_material(material_id)
        
        if sucesso:
            return (True, f"Material ID {material_id} deletado com sucesso.")
        else:
            # O Model já imprimiu o erro (ex: não encontrado)
            return (False, f"Erro ao deletar material ID {material_id}. Verifique o console.")
    
    except Exception as e:
        # O Model já trata o erro de FK, mas adicionamos um Catcher geral
        print(f"Controller Error: Erro ao deletar material. {e}")
        return (False, "Este material não pode ser deletado, pois pode estar em uso em uma OS ou orçamento.")


# --- FUNÇÃO EXISTENTE ---
def listar_materiais():
    """
    Controlador para buscar todos os materiais.
    (Neste caso simples, é apenas um repasse)
    """
    
    print("Controller: Solicitando lista de materiais ao Model.")
    try:
        materiais = estoque_model.get_all_materials()
        return (True, materiais) # (Sucesso, Dados)
    except Exception as e:
        print(f"Controller Error: Erro ao listar materiais. {e}")
        return (False, []) # (Sucesso, Dados)
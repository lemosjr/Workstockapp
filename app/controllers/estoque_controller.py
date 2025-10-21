from app.models import estoque_model
import decimal # Usaremos para validar o preço

"""
Camada Controller (Controlador) para Estoque.

Responsabilidade:
- Orquestrar a lógica de negócio.
- Fazer a ponte entre a View e o Model.
- Recebe dados da View, valida-os (lógica de negócio) e envia para o Model.
- Solicita dados ao Model e os envia para a View.
- NÃO deve conter código SQL (isso é do Model).
- NÃO deve conter código de interface (isso é da View).
"""

def salvar_material(data):
    """
    Controlador para salvar um novo material.
    'data' é um dicionário vindo da View.
    """
    
    # --- 1. Lógica de Negócio e Validação ---
    
    # Exemplo de validação: Nome é obrigatório
    if not data.get('nome') or len(data['nome'].strip()) == 0:
        print("Controller Error: O nome é obrigatório.")
        # Retornamos uma tupla: (Sucesso, Mensagem)
        return (False, "O nome do material é obrigatório.")

    # Exemplo de validação: SKU é obrigatório
    if not data.get('sku') or len(data['sku'].strip()) == 0:
        print("Controller Error: O SKU é obrigatório.")
        return (False, "O SKU do material é obrigatório.")
        
    # Exemplo de processamento: Garantir que valores numéricos sejam válidos
    try:
        # Se o preço vier vazio (None ou ""), definimos como 0.0
        preco = data.get('preco_custo')
        data['preco_custo'] = decimal.Decimal(preco if preco else 0.0)
        
        # Se o estoque vier vazio, definimos como 0
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

    # --- 2. Chamada ao Model ---
    
    # Se todas as validações passaram, tentamos criar no banco
    print(f"Controller: Dados validados. Enviando para o Model: {data}")
    
    novo_id = estoque_model.create_material(data)
    
    # --- 3. Resposta para a View ---
    
    if novo_id:
        return (True, f"Material '{data['nome']}' salvo com sucesso! (ID: {novo_id})")
    else:
        # O Model já imprimiu o erro específico (ex: "UNIQUE constraint failed")
        return (False, "Erro ao salvar o material no banco de dados. Verifique o console.")

def listar_materiais():
    """
    Controlador para buscar todos os materiais.
    (Neste caso simples, é apenas um repasse)
    """
    
    # Em um caso complexo, poderíamos ter lógica aqui
    # (ex: filtrar por permissão do usuário)
    
    print("Controller: Solicitando lista de materiais ao Model.")
    try:
        materiais = estoque_model.get_all_materials()
        return (True, materiais) # (Sucesso, Dados)
    except Exception as e:
        print(f"Controller Error: Erro ao listar materiais. {e}")
        return (False, []) # (Sucesso, Dados)
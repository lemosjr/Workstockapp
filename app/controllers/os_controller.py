from app.models import os_model
import datetime

"""
Camada Controller (Controlador) para Ordem de Serviço (OS).

Responsabilidade:
- Orquestrar a lógica de negócio das OS.
- Fazer a ponte entre a OS_View e o OS_Model.
- Validar dados vindos da View (lógica de negócio).
- Formatar dados para enviar ao Model.
"""

# Listas de valores válidos (baseados nos ENUMs do DB)
VALID_STATUS = ['aberta', 'em andamento', 'aguardando aprovação', 'concluída', 'cancelada']
VALID_PRIORIDADE = ['baixa', 'média', 'alta', 'urgente']


def salvar_os(data):
    """
    Controlador para salvar uma nova Ordem de Serviço.
    'data' é um dicionário vindo da View.
    """
    
    # --- 1. Lógica de Negócio e Validação ---
    
    # Validação de campos obrigatórios (baseado nos requisitos)
    if not data.get('tipo_servico') or len(data['tipo_servico'].strip()) == 0:
        print("Controller Error: O Tipo de Serviço é obrigatório.")
        return (False, "O Tipo de Serviço é obrigatório.") # 

    if not data.get('endereco') or len(data['endereco'].strip()) == 0:
        print("Controller Error: O Endereço é obrigatório.")
        return (False, "O Endereço do imóvel é obrigatório.") # 

    # Tratamento de dados opcionais e defaults
    data['descricao'] = data.get('descricao', '') # [cite: 36]
    
    # Valida e define defaults para Prioridade e Status
    data['prioridade'] = data.get('prioridade', 'baixa').lower()
    if data['prioridade'] not in VALID_PRIORIDADE:
        print(f"Controller Error: Prioridade inválida '{data['prioridade']}'.")
        return (False, f"Prioridade inválida. Use um de: {VALID_PRIORIDADE}") # 
        
    data['status'] = data.get('status', 'aberta').lower()
    if data['status'] not in VALID_STATUS:
        print(f"Controller Error: Status inválido '{data['status']}'.")
        return (False, f"Status inválido. Use um de: {VALID_STATUS}") # 
        
    # --- Validação e Formatação de Data ---
    data_prevista_str = data.get('data_conclusao_prevista')
    
    if data_prevista_str: # Se o usuário digitou uma data
        try:
            # Assume que a View envia no formato DD/MM/YYYY
            data_obj = datetime.datetime.strptime(data_prevista_str, '%d/%m/%Y').date()
            data['data_conclusao_prevista'] = data_obj
        except ValueError:
            print(f"Controller Error: Formato de data inválido '{data_prevista_str}'.")
            return (False, "Formato de data inválido. Use DD/MM/AAAA.") # 
    else:
        # Se veio vazio, definimos como Nulo
        data['data_conclusao_prevista'] = None

    # --- 2. Chamada ao Model ---
    
    print(f"Controller: Dados da OS validados. Enviando para o Model...")
    
    novo_id = os_model.create_os(data)
    
    # --- 3. Resposta para a View ---
    
    if novo_id:
        msg = f"OS #{novo_id} (Tipo: {data['tipo_servico']}) salva com sucesso!"
        return (True, msg)
    else:
        return (False, "Erro ao salvar a OS no banco de dados. Verifique o console.")

def listar_os():
    """
    Controlador para buscar todas as Ordens de Serviço.
    """
    print("Controller: Solicitando lista de OS ao Model.")
    try:
        ordens = os_model.get_all_os()
        return (True, ordens) # (Sucesso, Dados)
    except Exception as e:
        print(f"Controller Error: Erro ao listar OS. {e}")
        return (False, []) # (Sucesso, Dados)
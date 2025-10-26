from app.models import os_model
import datetime

"""
Camada Controller (Controlador) para Ordem de Serviço (OS).
Refatorado para incluir lógica de Update (Atualização).
"""

# Listas de valores válidos (baseados nos ENUMs do DB)
VALID_STATUS = ['aberta', 'em andamento', 'aguardando aprovação', 'concluída', 'cancelada']
VALID_PRIORIDADE = ['baixa', 'média', 'alta', 'urgente']


def _validar_e_formatar_dados_os(data):
    """
    Função auxiliar PRIVADA para validar e formatar dados da OS.
    Usada tanto para criar (salvar) quanto para atualizar.
    Retorna (True, dados_formatados) ou (False, mensagem_erro).
    """
    
    # 1. Validação de campos obrigatórios
    if not data.get('tipo_servico') or len(data['tipo_servico'].strip()) == 0:
        print("Controller Error: O Tipo de Serviço é obrigatório.")
        return (False, "O Tipo de Serviço é obrigatório.")

    if not data.get('endereco') or len(data['endereco'].strip()) == 0:
        print("Controller Error: O Endereço é obrigatório.")
        return (False, "O Endereço do imóvel é obrigatório.")

    # 2. Tratamento de dados opcionais e defaults
    data['descricao'] = data.get('descricao', '')
    
    data['prioridade'] = data.get('prioridade', 'baixa').lower()
    if data['prioridade'] not in VALID_PRIORIDADE:
        print(f"Controller Error: Prioridade inválida '{data['prioridade']}'.")
        return (False, f"Prioridade inválida. Use um de: {VALID_PRIORIDADE}")
        
    data['status'] = data.get('status', 'aberta').lower()
    if data['status'] not in VALID_STATUS:
        print(f"Controller Error: Status inválido '{data['status']}'.")
        return (False, f"Status inválido. Use um de: {VALID_STATUS}")
        
    # 3. Validação e Formatação de Data (String -> Objeto Date)
    data_prevista_str = data.get('data_conclusao_prevista')
    
    if data_prevista_str: # Se o usuário digitou uma data
        try:
            # Converte a string "DD/MM/YYYY" em um objeto date
            data_obj = datetime.datetime.strptime(data_prevista_str, '%d/%m/%Y').date()
            data['data_conclusao_prevista'] = data_obj
        except ValueError:
            print(f"Controller Error: Formato de data inválido '{data_prevista_str}'.")
            return (False, "Formato de data inválido. Use DD/MM/AAAA.")
    else:
        data['data_conclusao_prevista'] = None

    # Se todas as validações passaram
    return (True, data)


# --- FUNÇÃO ATUALIZADA (Refatorada) ---
def salvar_os(data):
    """
    Controlador para salvar uma NOVA Ordem de Serviço.
    """
    
    # 1. Validação e Formatação
    sucesso_validacao, dados_ou_erro = _validar_e_formatar_dados_os(data)
    
    if not sucesso_validacao:
        return (False, dados_ou_erro) # Retorna a mensagem de erro
    
    # 'dados_ou_erro' agora contém os dados formatados
    dados_formatados = dados_ou_erro

    # 2. Chamada ao Model
    print(f"Controller: Dados da OS validados. Enviando para o Model (Create)...")
    novo_id = os_model.create_os(dados_formatados)
    
    # 3. Resposta para a View
    if novo_id:
        msg = f"OS #{novo_id} (Tipo: {dados_formatados['tipo_servico']}) salva com sucesso!"
        return (True, msg)
    else:
        return (False, "Erro ao salvar a OS no banco de dados. Verifique o console.")

# --- FUNÇÃO NOVA ---
def atualizar_os(os_id, data):
    """
    Controlador para ATUALIZAR uma Ordem de Serviço existente.
    """
    
    # 1. Validação e Formatação (REUTILIZANDO a função)
    sucesso_validacao, dados_ou_erro = _validar_e_formatar_dados_os(data)
    
    if not sucesso_validacao:
        return (False, dados_ou_erro) # Retorna a mensagem de erro
    
    dados_formatados = dados_ou_erro

    # 2. Chamada ao Model
    print(f"Controller: Dados da OS validados. Enviando para o Model (Update)...")
    sucesso_update = os_model.update_os(os_id, dados_formatados)
    
    # 3. Resposta para a View
    if sucesso_update:
        msg = f"OS #{os_id} (Tipo: {dados_formatados['tipo_servico']}) atualizada com sucesso!"
        return (True, msg)
    else:
        return (False, f"Erro ao atualizar a OS #{os_id}. Verifique o console.")

# --- FUNÇÃO NOVA ---
def buscar_os_por_id(os_id):
    """
    Controlador para buscar os dados de UMA OS específica.
    Usado para preencher o formulário de edição.
    """
    print(f"Controller: Buscando dados da OS #{os_id}.")
    try:
        os_data = os_model.get_os_by_id(os_id)
        
        if os_data:
            # Converte o DictRow (retorno do Model) para um dict padrão
            dados_formatados = dict(os_data)
            
            # Formata os dados de volta para a View (Objeto Date -> String)
            # A View só entende strings
            if dados_formatados.get('data_conclusao_prevista'):
                dados_formatados['data_conclusao_prevista'] = dados_formatados['data_conclusao_prevista'].strftime('%d/%m/%Y')
            else:
                dados_formatados['data_conclusao_prevista'] = "" # Envia string vazia
            
            return (True, dados_formatados)
        else:
            return (False, f"Nenhuma OS encontrada com o ID {os_id}.")
            
    except Exception as e:
        print(f"Controller Error: Erro ao buscar OS por ID. {e}")
        return (False, "Erro ao buscar dados da OS. Verifique o console.")

# --- FUNÇÃO INALTERADA ---
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
    
# --- FUNÇÃO NOVA ---
def deletar_os(os_id):
    """
    Controlador para deletar uma Ordem de Serviço.
    """
    if not os_id:
        return (False, "Nenhuma OS selecionada para deletar.")
        
    print(f"Controller: Solicitando exclusão da OS ID #{os_id}.")
    
    try:
        sucesso = os_model.delete_os(os_id)
        
        if sucesso:
            return (True, f"Ordem de Serviço ID {os_id} deletada com sucesso.")
        else:
            # O Model já imprimiu o erro
            return (False, f"Erro ao deletar a OS ID {os_id}. Verifique o console.")
    
    except Exception as e:
        print(f"Controller Error: Erro ao deletar OS. {e}")
        # Mensagem amigável para o caso de FK (Foreign Key)
        return (False, "Esta OS não pode ser deletada, pois pode ter orçamentos ou materiais vinculados.")
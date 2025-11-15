from app.models import os_model
from app.models import estoque_model # Necessário para o vínculo de materiais
import datetime
import decimal # Necessário para o orçamento
import re # (Não usado aqui, mas bom manter caso adicione validação de e-mail)

"""
Camada Controller (Controlador) para Ordem de Serviço (OS).
Versão completa com CRUD, Vínculo de Materiais, Orçamento e Aprovação.
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


# --- Seção 1: CRUD Básico da OS ---

def salvar_os(data):
    """
    Controlador para salvar uma NOVA Ordem de Serviço.
    """
    sucesso_validacao, dados_ou_erro = _validar_e_formatar_dados_os(data)
    
    if not sucesso_validacao:
        return (False, dados_ou_erro) # Retorna a mensagem de erro
    
    dados_formatados = dados_ou_erro

    print(f"Controller: Dados da OS validados. Enviando para o Model (Create)...")
    novo_id = os_model.create_os(dados_formatados)
    
    if novo_id:
        msg = f"OS #{novo_id} (Tipo: {dados_formatados['tipo_servico']}) salva com sucesso!"
        return (True, msg)
    else:
        return (False, "Erro ao salvar a OS no banco de dados. Verifique o console.")

def atualizar_os(os_id, data):
    """
    Controlador para ATUALIZAR uma Ordem de Serviço existente.
    """
    sucesso_validacao, dados_ou_erro = _validar_e_formatar_dados_os(data)
    
    if not sucesso_validacao:
        return (False, dados_ou_erro) # Retorna a mensagem de erro
    
    dados_formatados = dados_ou_erro

    print(f"Controller: Dados da OS validados. Enviando para o Model (Update)...")
    sucesso_update = os_model.update_os(os_id, dados_formatados)
    
    if sucesso_update:
        msg = f"OS #{os_id} (Tipo: {dados_formatados['tipo_servico']}) atualizada com sucesso!"
        return (True, msg)
    else:
        return (False, f"Erro ao atualizar a OS #{os_id}. Verifique o console.")

def buscar_os_por_id(os_id):
    """
    Controlador para buscar os dados de UMA OS específica.
    Usado para preencher o formulário de edição.
    """
    print(f"Controller: Buscando dados da OS #{os_id}.")
    try:
        os_data = os_model.get_os_by_id(os_id)
        
        if os_data:
            dados_formatados = dict(os_data)
            
            # Formata os dados de volta para a View (Objeto Date -> String)
            if dados_formatados.get('data_conclusao_prevista'):
                dados_formatados['data_conclusao_prevista'] = dados_formatados['data_conclusao_prevista'].strftime('%d/%m/%Y')
            else:
                dados_formatados['data_conclusao_prevista'] = ""
            
            return (True, dados_formatados)
        else:
            return (False, f"Nenhuma OS encontrada com o ID {os_id}.")
            
    except Exception as e:
        print(f"Controller Error: Erro ao buscar OS por ID. {e}")
        return (False, "Erro ao buscar dados da OS. Verifique o console.")

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
        return (False, [])

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
            return (False, f"Erro ao deletar a OS ID {os_id}. Verifique o console.")
    
    except Exception as e:
        print(f"Controller Error: Erro ao deletar OS. {e}")
        return (False, "Esta OS não pode ser deletada, pois pode ter orçamentos ou materiais vinculados.")


# --- Seção 2: Vínculo OS <-> Material ---

def listar_materiais_da_os(os_id):
    """
    Controlador para buscar a lista de materiais de uma OS.
    """
    if not os_id:
        return (False, [])
        
    print(f"Controller: Listando materiais da OS #{os_id}.")
    try:
        materiais = os_model.get_materiais_for_os(os_id)
        return (True, materiais)
    except Exception as e:
        print(f"Controller Error: Erro ao listar materiais da OS: {e}")
        return (False, [])

def vincular_material_os(os_id, material_id, quantidade):
    """
    Controlador para vincular um material a uma OS e
    dar BAIXA no estoque.
    """
    try:
        quantidade_num = int(quantidade)
        if quantidade_num <= 0:
            return (False, "A quantidade deve ser maior que zero.")
    except ValueError:
        return (False, "Quantidade inválida.")

    material_data = estoque_model.get_material_by_id(material_id)
    if not material_data:
        return (False, "Erro: Material não encontrado no estoque.")
        
    estoque_atual = material_data['estoque_atual']
    preco_custo = material_data['preco_custo']
    material_nome = material_data['nome']

    if quantidade_num > estoque_atual:
        msg = (f"Estoque insuficiente para '{material_nome}'.\n"
               f"Disponível: {estoque_atual} | Solicitado: {quantidade_num}")
        return (False, msg)

    print(f"Controller: Adicionando {quantidade_num} de '{material_nome}' (R${preco_custo}) na OS {os_id}...")
    novo_id_vinculo = os_model.add_material_to_os(os_id, material_id, quantidade_num, preco_custo)
    
    if not novo_id_vinculo:
        return (False, f"O material '{material_nome}' já está adicionado nesta OS. (Atualize a quantidade se desejar).")

    nova_quantidade_estoque = estoque_atual - quantidade_num
    print(f"Controller: Dando baixa no estoque de '{material_nome}'. (Atual: {estoque_atual} -> Nova: {nova_quantidade_estoque})")
    sucesso_baixa = estoque_model.update_material_estoque(material_id, nova_quantidade_estoque)
    
    if sucesso_baixa:
        return (True, f"'{material_nome}' adicionado à OS e estoque atualizado!")
    else:
        print(f"Controller CRÍTICO: Material ID {material_id} foi adicionado à OS {os_id}, MAS falhou ao dar baixa no estoque.")
        return (False, "Material adicionado à OS, mas falhou ao atualizar o estoque.")


def desvincular_material_os(os_material_id, material_id, quantidade_removida):
    """
    Controlador para remover um material de uma OS e
    ESTORNAR (devolver) o item ao estoque.
    """
    material_data = estoque_model.get_material_by_id(material_id)
    if not material_data:
        return (False, "Erro: Material não encontrado no estoque.")
        
    estoque_atual = material_data['estoque_atual']
    material_nome = material_data['nome']

    print(f"Controller: Removendo vínculo ID {os_material_id} da OS...")
    sucesso_remocao = os_model.remove_material_from_os(os_material_id)
    
    if not sucesso_remocao:
        return (False, "Erro ao remover o material da OS.")

    nova_quantidade_estoque = estoque_atual + int(quantidade_removida)
    print(f"Controller: Estornando {quantidade_removida} de '{material_nome}' ao estoque. (Atual: {estoque_atual} -> Nova: {nova_quantidade_estoque})")
    sucesso_estorno = estoque_model.update_material_estoque(material_id, nova_quantidade_estoque)
    
    if sucesso_estorno:
        return (True, f"'{material_nome}' removido da OS e estoque estornado!")
    else:
        print(f"Controller CRÍTICO: Material ID {material_id} foi removido da OS, MAS falhou ao estornar o estoque.")
        return (False, "Material removido da OS, mas falhou ao atualizar o estoque.")


# --- Seção 3: Lógica de Orçamento ---

def get_orcamento_os(os_id):
    """
    Busca os dados de orçamento atuais de uma OS.
    """
    if not os_id:
        return (False, "ID da OS inválido.")
        
    print(f"Controller: Buscando dados de orçamento da OS #{os_id}.")
    try:
        os_data = os_model.get_os_by_id(os_id)
        if os_data:
            orcamento_data = {
                "materiais": os_data['orcamento_materiais'],
                "mao_de_obra": os_data['orcamento_mao_de_obra'],
                "total": os_data['orcamento_total']
            }
            return (True, orcamento_data)
        else:
            return (False, "OS não encontrada.")
            
    except Exception as e:
        print(f"Controller Error: Erro ao buscar orçamento da OS: {e}")
        return (False, "Erro ao buscar dados.")


def recalcular_e_salvar_orcamento_os(os_id, custo_mao_de_obra_str):
    """
    Processo principal do orçamento:
    1. Calcula o custo total dos materiais vinculados.
    2. Valida o custo de mão de obra inserido.
    3. Soma tudo e salva no banco de dados.
    """
    if not os_id:
        return (False, "ID da OS inválido.")
        
    # 1. Calcular Custo dos Materiais
    try:
        materiais_vinculados = os_model.get_materiais_for_os(os_id)
        total_custo_materiais = decimal.Decimal(0.0)
        
        for item in materiais_vinculados:
            total_custo_materiais += (item['preco_custo_na_data'] * item['quantidade'])
        print(f"Controller: Custo total de materiais calculado: R$ {total_custo_materiais}")
        
    except Exception as e:
        print(f"Controller Error: Erro ao calcular custo de materiais: {e}")
        return (False, "Erro ao calcular o custo dos materiais.")

    # 2. Validar Custo de Mão de Obra
    try:
        custo_mao_de_obra = decimal.Decimal(custo_mao_de_obra_str if custo_mao_de_obra_str else 0.0)
        if custo_mao_de_obra < 0:
            return (False, "Custo de Mão de Obra não pode ser negativo.")
    except (decimal.InvalidOperation, ValueError):
        return (False, "Valor de Mão de Obra inválido.")
        
    # 3. Calcular Total e Salvar no Model
    custo_total_orcamento = total_custo_materiais + custo_mao_de_obra
    print(f"Controller: Salvando orçamento... Mat: {total_custo_materiais}, M.O: {custo_mao_de_obra}, Total: {custo_total_orcamento}")
    
    sucesso_save = os_model.update_os_orcamento(
        os_id=os_id,
        custo_materiais=total_custo_materiais,
        custo_mao_de_obra=custo_mao_de_obra,
        custo_total=custo_total_orcamento
    )
    
    if sucesso_save:
        return (True, "Orçamento recalculado e salvo com sucesso!")
    else:
        return (False, "Erro ao salvar o orçamento no banco de dados.")


# --- Seção 4: Fluxo de Aprovação ---

def enviar_orcamento_para_aprovacao(os_id):
    """
    Controlador para a 'Empresa' enviar o orçamento para o proprietário.
    """
    if not os_id:
        return (False, "ID da OS inválido.")

    # Lógica de Negócio: Verificar se o orçamento já foi calculado
    sucesso_get, data_orcamento = get_orcamento_os(os_id)
    if not sucesso_get or data_orcamento['total'] <= 0:
        return (False, "Não é possível enviar. O orçamento ainda não foi calculado ou está zerado.")

    print(f"Controller: Enviando orçamento da OS #{os_id} para aprovação.")
    
    sucesso = os_model.set_os_orcamento_enviado(os_id)
    
    if sucesso:
        return (True, "Orçamento enviado para aprovação com sucesso!")
    else:
        return (False, "Erro ao enviar orçamento.")

def aprovar_orcamento_os(os_id):
    """
    Controlador para o 'Proprietário' aprovar um orçamento.
    """
    if not os_id:
        return (False, "ID da OS inválido.")
        
    print(f"Controller: Aprovando orçamento da OS #{os_id}.")
    
    # Lógica de Negócio: Ao aprovar, o status muda para 'em andamento'
    novo_status = 'em andamento' 
    
    sucesso = os_model.set_os_orcamento_aprovado(os_id, novo_status)
    
    if sucesso:
        return (True, "Orçamento aprovado! O status da OS foi atualizado para 'Em Andamento'.")
    else:
        return (False, "Erro ao aprovar o orçamento.")

def rejeitar_orcamento_os(os_id):
    """
    Controlador para o 'Proprietário' rejeitar um orçamento.
    """
    if not os_id:
        return (False, "ID da OS inválido.")
        
    print(f"Controller: Rejeitando orçamento da OS #{os_id}.")
    
    # Lógica de Negócio: Ao rejeitar, o status volta para 'aberta' (para re-edição)
    novo_status = 'aberta'
    
    sucesso = os_model.update_os_status(os_id, novo_status)
    
    if sucesso:
        return (True, "Orçamento rejeitado. O status da OS voltou para 'Aberta'.")
    else:
        return (False, "Erro ao rejeitar o orçamento.")
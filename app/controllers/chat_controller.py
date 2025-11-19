from app.models import chat_model
import datetime

"""
Camada Controller (Controlador) para o Chat.

Responsabilidade:
- Validar envio de mensagens.
- Buscar histórico de mensagens.
- Formatar datas para exibição amigável na View.
"""

def enviar_mensagem(os_id, remetente_id, conteudo):
    """
    Controlador para enviar uma mensagem.
    """
    # 1. Validação
    if not conteudo or len(conteudo.strip()) == 0:
        return (False, "A mensagem não pode estar vazia.")
    
    if not os_id or not remetente_id:
        return (False, "Erro interno: ID da OS ou Usuário inválido.")

    # 2. Chama o Model
    print(f"Controller (Chat): Enviando mensagem na OS #{os_id}...")
    novo_id = chat_model.create_message(os_id, remetente_id, conteudo.strip())
    
    if novo_id:
        return (True, "Mensagem enviada.")
    else:
        return (False, "Erro ao enviar mensagem.")

def buscar_chat_os(os_id):
    """
    Busca o histórico de mensagens e FORMATA os dados para a View.
    """
    if not os_id:
        return (False, [])
        
    print(f"Controller (Chat): Buscando histórico da OS #{os_id}...")
    
    mensagens_raw = chat_model.get_messages_by_os(os_id)
    mensagens_formatadas = []
    
    # Formata os dados para facilitar a vida da View
    for msg in mensagens_raw:
        # Converte datetime para string "DD/MM/YYYY HH:MM"
        data_obj = msg['data_envio']
        data_fmt = data_obj.strftime('%d/%m %H:%M') if data_obj else "--/--"
        
        # Cria um dicionário limpo para a View
        msg_dict = {
            'id': msg['id'],
            'remetente_id': msg['remetente_id'],
            'nome': msg['remetente_nome'] or "Usuário Desconhecido", # Caso tenha sido deletado
            'perfil': msg['remetente_perfil'],
            'texto': msg['conteudo'],
            'data': data_fmt
        }
        mensagens_formatadas.append(msg_dict)
        
    return (True, mensagens_formatadas)
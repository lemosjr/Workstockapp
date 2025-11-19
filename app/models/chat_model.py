from app.utils.db_connector import get_connection, release_connection
import psycopg2
from psycopg2 import extras

"""
Camada Model (Modelo) para o Chat.

Responsabilidade:
- Salvar mensagens no banco de dados.
- Buscar histórico de mensagens de uma OS (trazendo o nome do remetente).
"""

def create_message(os_id, remetente_id, conteudo):
    """
    Salva uma nova mensagem no banco de dados.
    """
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        query = """
        INSERT INTO mensagens (os_id, remetente_id, conteudo)
        VALUES (%s, %s, %s)
        RETURNING id;
        """
        
        cursor.execute(query, (os_id, remetente_id, conteudo))
        new_id = cursor.fetchone()[0]
        conn.commit()
        
        print(f"Model (Chat): Mensagem enviada na OS #{os_id} pelo User #{remetente_id}.")
        return new_id
        
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Model Error (Chat): Erro ao salvar mensagem: {error}")
        if conn:
            conn.rollback()
        return None
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            release_connection(conn)

def get_messages_by_os(os_id):
    """
    Busca todas as mensagens de uma OS, ordenadas por data.
    Faz um JOIN com a tabela de usuários para pegar o nome do remetente.
    """
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=extras.DictCursor)
        
        # Query Inteligente:
        # Trazemos as colunas da mensagem E a coluna 'nome_completo' do usuário.
        # Usamos 'LEFT JOIN' para que, se o usuário foi deletado (id nulo),
        # a mensagem ainda venha (com nome nulo).
        query = """
        SELECT 
            m.id,
            m.os_id,
            m.remetente_id,
            m.conteudo,
            m.data_envio,
            u.nome_completo as remetente_nome,
            u.perfil as remetente_perfil
        FROM mensagens AS m
        LEFT JOIN usuarios AS u ON m.remetente_id = u.id
        WHERE m.os_id = %s
        ORDER BY m.data_envio ASC;
        """
        
        cursor.execute(query, (os_id,))
        mensagens = cursor.fetchall()
        return mensagens # Lista de dicionários
        
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Model Error (Chat): Erro ao buscar mensagens: {error}")
        return []
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            release_connection(conn)
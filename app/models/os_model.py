from app.utils.db_connector import get_connection, release_connection
import psycopg2
from psycopg2 import extras # Para retornar dicts

"""
Camada Model (Modelo) para Ordem de Serviço (OS).

Responsabilidade:
- Conter TODA a lógica de banco de dados (queries SQL)
- Funções para Criar, Ler, Atualizar e Deletar (CRUD) Ordens de Serviço.
"""

def create_os(data):
    """
    Cria uma nova Ordem de Serviço no banco de dados.
    'data' é um dicionário contendo as chaves:
    'tipo_servico', 'endereco', 'descricao', 'prioridade', 
    'status', 'data_conclusao_prevista'
    """
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        query = """
        INSERT INTO ordens_servico (
            tipo_servico, endereco, descricao, prioridade, 
            status, data_conclusao_prevista
        ) VALUES (
            %(tipo_servico)s, %(endereco)s, %(descricao)s, %(prioridade)s,
            %(status)s, %(data_conclusao_prevista)s
        ) RETURNING id;
        """
        
        cursor.execute(query, data)
        
        new_id = cursor.fetchone()[0]
        conn.commit()
        
        print(f"OS criada com sucesso. ID: {new_id}")
        return new_id
        
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Erro ao criar OS: {error}")
        if conn:
            conn.rollback()
        return None
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            release_connection(conn)

def get_all_os():
    """
    Busca todas as OS cadastradas, ordenadas pela mais recente.
    Retorna uma lista de dicionários.
    """
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=extras.DictCursor)
        
        # Ordena por ID decrescente (mais novas primeiro)
        query = "SELECT * FROM ordens_servico ORDER BY id DESC;"
        cursor.execute(query)
        
        ordens = cursor.fetchall()
        return ordens
        
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Erro ao buscar Ordens de Serviço: {error}")
        return []
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            release_connection(conn)

def get_os_by_id(os_id):
    """
    Busca uma Ordem de Serviço específica pelo seu ID.
    Retorna um dicionário (DictRow).
    """
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=extras.DictCursor)
        
        query = "SELECT * FROM ordens_servico WHERE id = %s;"
        cursor.execute(query, (os_id,)) # Passa o ID como uma tupla
        
        os_data = cursor.fetchone() # Pega apenas um resultado
        return os_data
        
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Erro ao buscar OS por ID ({os_id}): {error}")
        return None
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            release_connection(conn)

def update_os(os_id, data):
    """
    Atualiza uma Ordem de Serviço existente no banco de dados.
    'data' é um dicionário contendo os campos a serem atualizados.
    'os_id' é o ID da OS a ser modificada.
    """
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        query = """
        UPDATE ordens_servico SET
            tipo_servico = %(tipo_servico)s,
            endereco = %(endereco)s,
            descricao = %(descricao)s,
            prioridade = %(prioridade)s,
            status = %(status)s,
            data_conclusao_prevista = %(data_conclusao_prevista)s,
            data_atualizacao = CURRENT_TIMESTAMP
        WHERE
            id = %(os_id)s;
        """
        
        # Adicionamos o os_id ao dicionário de dados para a query
        data['os_id'] = os_id
        
        cursor.execute(query, data)
        conn.commit()
        
        print(f"OS ID: {os_id} atualizada com sucesso.")
        return True # Retorna sucesso
        
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Erro ao atualizar OS ({os_id}): {error}")
        if conn:
            conn.rollback()
        return False # Retorna falha
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            release_connection(conn)
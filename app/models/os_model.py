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

def delete_os(os_id):
    """
    Deleta uma Ordem de Serviço do banco de dados usando seu ID.
    """
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        query = "DELETE FROM ordens_servico WHERE id = %s;"
        
        cursor.execute(query, (os_id,))
        conn.commit() # Confirma a transação
        
        # Verifica se alguma linha foi realmente deletada
        if cursor.rowcount > 0:
            print(f"Model (OS): OS ID {os_id} deletada com sucesso.")
            return True
        else:
            print(f"Model (OS): NENHUMA OS encontrada com ID {os_id}.")
            return False # Nenhuma linha foi afetada
        
    except (Exception, psycopg2.DatabaseError) as error:
        # Futuramente, se a OS tiver materiais (FK), o erro será capturado aqui.
        print(f"Model Error (OS): Erro ao deletar OS: {error}")
        if conn:
            conn.rollback() # Desfaz a transação
        return False
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            release_connection(conn)

def add_material_to_os(os_id, material_id, quantidade, preco_custo):
    """
    Adiciona um novo material (e sua quantidade) a uma OS.
    Grava o preço do custo no momento da adição.
    """
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        query = """
        INSERT INTO os_materiais (os_id, material_id, quantidade, preco_custo_na_data)
        VALUES (%s, %s, %s, %s)
        RETURNING id;
        """
        
        cursor.execute(query, (os_id, material_id, quantidade, preco_custo))
        new_id = cursor.fetchone()[0]
        conn.commit()
        
        print(f"Model (OS-Material): Material ID {material_id} adicionado à OS ID {os_id}.")
        return new_id
        
    except psycopg2.IntegrityError as e:
        # Captura o erro da 'UNIQUE constraint (os_id, material_id)'
        print(f"Model Error (OS-Material): Item já existe na OS. {e}")
        if conn:
            conn.rollback()
        return None # Indica falha por duplicidade
        
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Model Error (OS-Material): Erro ao adicionar material: {error}")
        if conn:
            conn.rollback()
        return None
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            release_connection(conn)

def get_materiais_for_os(os_id):
    """
    Busca a lista de materiais vinculados a uma OS específica.
    Usa JOIN para trazer os nomes e SKUs dos materiais.
    """
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=extras.DictCursor)
        
        # Esta query é o coração: ela junta as 3 tabelas
        query = """
        SELECT 
            osm.id as os_material_id, -- ID da linha na tabela 'os_materiais'
            m.id as material_id,
            m.nome as material_nome,
            m.sku,
            osm.quantidade,
            osm.preco_custo_na_data
        FROM os_materiais AS osm
        JOIN materiais AS m ON osm.material_id = m.id
        WHERE osm.os_id = %s;
        """
        
        cursor.execute(query, (os_id,))
        materiais = cursor.fetchall()
        return materiais # Lista de dicionários
        
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Model Error (OS-Material): Erro ao buscar materiais da OS: {error}")
        return []
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            release_connection(conn)

def remove_material_from_os(os_material_id):
    """
    Remove uma linha da tabela 'os_materiais' pelo ID único dela.
    (os_material_id é o 'osm.id' da query anterior)
    """
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        query = "DELETE FROM os_materiais WHERE id = %s;"
        
        cursor.execute(query, (os_material_id,))
        conn.commit()
        return cursor.rowcount > 0 # True se deletou
        
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Model Error (OS-Material): Erro ao remover material da OS: {error}")
        if conn:
            conn.rollback()
        return False
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            release_connection(conn)

def update_material_quantidade_in_os(os_material_id, nova_quantidade):
    """
    Atualiza a quantidade de um material já vinculado a uma OS.
    """
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        query = "UPDATE os_materiais SET quantidade = %s WHERE id = %s;"
        
        cursor.execute(query, (nova_quantidade, os_material_id))
        conn.commit()
        return cursor.rowcount > 0 # True se atualizou
        
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Model Error (OS-Material): Erro ao atualizar quantidade: {error}")
        if conn:
            conn.rollback()
        return False
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            release_connection(conn)

def update_os_orcamento(os_id, custo_materiais, custo_mao_de_obra, custo_total):
    """
    Atualiza os campos de orçamento de uma OS específica.
    """
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        query = """
        UPDATE ordens_servico SET
            orcamento_materiais = %s,
            orcamento_mao_de_obra = %s,
            orcamento_total = %s,
            data_atualizacao = CURRENT_TIMESTAMP
        WHERE
            id = %s;
        """
        
        cursor.execute(query, (custo_materiais, custo_mao_de_obra, custo_total, os_id))
        conn.commit()
        
        if cursor.rowcount > 0:
            print(f"Model (OS): Orçamento da OS ID {os_id} atualizado.")
            return True
        else:
            print(f"Model (OS): OS ID {os_id} não encontrada para atualizar orçamento.")
            return False

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Model Error (OS): Erro ao atualizar orçamento: {error}")
        if conn:
            conn.rollback()
        return False
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            release_connection(conn)

def update_os_status(os_id, novo_status):
    """
    Função genérica para atualizar o STATUS de uma OS.
    Usada para Enviar, Aprovar, Rejeitar, etc.
    """
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        query = "UPDATE ordens_servico SET status = %s WHERE id = %s;"
        
        cursor.execute(query, (novo_status, os_id))
        conn.commit()
        return cursor.rowcount > 0

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Model Error (OS): Erro ao atualizar status: {error}")
        if conn: conn.rollback()
        return False
    finally:
        if cursor: cursor.close()
        if conn: release_connection(conn)

def set_os_orcamento_enviado(os_id):
    """
    Define o status como 'aguardando aprovação' e salva a data de envio.
    """
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        query = """
        UPDATE ordens_servico SET 
            status = 'aguardando aprovação',
            data_orcamento_enviado = CURRENT_TIMESTAMP
        WHERE id = %s;
        """
        
        cursor.execute(query, (os_id,))
        conn.commit()
        return cursor.rowcount > 0

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Model Error (OS): Erro ao enviar orçamento: {error}")
        if conn: conn.rollback()
        return False
    finally:
        if cursor: cursor.close()
        if conn: release_connection(conn)

def set_os_orcamento_aprovado(os_id, novo_status):
    """
    Define o status (ex: 'em andamento') e salva a data de aprovação.
    """
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        query = """
        UPDATE ordens_servico SET 
            status = %s,
            data_aprovacao = CURRENT_TIMESTAMP
        WHERE id = %s;
        """
        
        cursor.execute(query, (novo_status, os_id))
        conn.commit()
        return cursor.rowcount > 0

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Model Error (OS): Erro ao aprovar orçamento: {error}")
        if conn: conn.rollback()
        return False
    finally:
        if cursor: cursor.close()
        if conn: release_connection(conn)
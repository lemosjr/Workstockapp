from app.utils.db_connector import get_connection, release_connection
import psycopg2
from psycopg2 import extras # Para retornar dicts

"""
Camada Model (Modelo) para Estoque.

Responsabilidade:
- Conter TODA a lógica de banco de dados (queries SQL)
- Funções para Criar, Ler, Atualizar e Deletar (CRUD) materiais.
- NÃO deve conter lógica de negócio (isso é do Controller).
- NÃO deve conter código de interface (isso é da View).
"""

def create_material(data):
    """
    Cria um novo material no banco de dados.
    'data' é um dicionário contendo as chaves:
    'nome', 'sku', 'unidade_medida', 'preco_custo', 
    'estoque_atual', 'estoque_minimo', 'fornecedor', 'localizacao'
    """
    conn = None
    cursor = None
    try:
        conn = get_connection() # Pega uma conexão do pool
        cursor = conn.cursor()
        
        query = """
        INSERT INTO materiais (
            nome, sku, unidade_medida, preco_custo, 
            estoque_atual, estoque_minimo, fornecedor_preferencial, localizacao
        ) VALUES (
            %(nome)s, %(sku)s, %(unidade_medida)s, %(preco_custo)s, 
            %(estoque_atual)s, %(estoque_minimo)s, %(fornecedor)s, %(localizacao)s
        ) RETURNING id;
        """
        
        # O psycopg2 faz o "sanitize" (limpeza) dos dados, evitando SQL Injection
        cursor.execute(query, data)
        
        new_id = cursor.fetchone()[0] # Pega o ID do material recém-criado
        conn.commit() # Confirma a transação
        
        print(f"Material criado com sucesso. ID: {new_id}")
        return new_id
        
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Erro ao criar material: {error}")
        if conn:
            conn.rollback() # Desfaz a transação em caso de erro
        return None
        
    finally:
        # Garante que a conexão seja devolvida ao pool, ocorrendo erro ou não
        if cursor:
            cursor.close()
        if conn:
            release_connection(conn) # Devolve a conexão

def get_all_materials():
    """
    Busca todos os materiais cadastrados, ordenados por nome.
    Retorna uma lista de dicionários.
    """
    conn = None
    cursor = None
    try:
        conn = get_connection()
        # Usamos DictCursor para que o resultado venha como dicionário (ex: {'id': 1, 'nome': 'Tinta'})
        # em vez de tupla (ex: (1, 'Tinta'))
        cursor = conn.cursor(cursor_factory=extras.DictCursor)
        
        query = "SELECT * FROM materiais ORDER BY nome ASC;"
        cursor.execute(query)
        
        materiais = cursor.fetchall()
        return materiais # Lista de dicts
        
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Erro ao buscar materiais: {error}")
        return [] # Retorna lista vazia em caso de erro
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            release_connection(conn)

# --- FUNÇÕES ATUALIZADAS (CRUD COMPLETO) ---

def get_material_by_id(material_id):
    """ Busca um material pelo seu ID. Retorna um dict. """
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=extras.DictCursor)
        
        query = "SELECT * FROM materiais WHERE id = %s;"
        cursor.execute(query, (material_id,))
        
        material = cursor.fetchone()
        return material
        
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Erro ao buscar material por ID ({material_id}): {error}")
        return None
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            release_connection(conn)

def update_material(material_id, data):
    """ 
    Atualiza um material existente. 
    'data' deve conter as mesmas chaves de 'create_material'.
    """
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Adiciona o ID ao dicionário para a query
        data['id'] = material_id
        
        query = """
        UPDATE materiais SET
            nome = %(nome)s,
            sku = %(sku)s,
            unidade_medida = %(unidade_medida)s,
            preco_custo = %(preco_custo)s,
            estoque_atual = %(estoque_atual)s,
            estoque_minimo = %(estoque_minimo)s,
            fornecedor_preferencial = %(fornecedor)s,
            localizacao = %(localizacao)s,
            data_atualizacao = CURRENT_TIMESTAMP
        WHERE
            id = %(id)s;
        """
        
        cursor.execute(query, data)
        conn.commit()
        
        # Verifica se alguma linha foi realmente atualizada
        if cursor.rowcount > 0:
            print(f"Model (Estoque): Material ID {material_id} atualizado com sucesso.")
            return True
        else:
            print(f"Model (Estoque): NENHUM material encontrado com ID {material_id} para atualizar.")
            return False # Nenhuma linha foi afetada

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Erro ao atualizar material: {error}")
        if conn:
            conn.rollback()
        return False
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            release_connection(conn)

def delete_material(material_id):
    """
    Deleta um material do banco de dados usando seu ID.
    """
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        query = "DELETE FROM materiais WHERE id = %s;"
        
        cursor.execute(query, (material_id,))
        conn.commit() # Confirma a transação
        
        # Verifica se alguma linha foi realmente deletada
        if cursor.rowcount > 0:
            print(f"Model (Estoque): Material ID {material_id} deletado com sucesso.")
            return True
        else:
            print(f"Model (Estoque): NENHUM material encontrado com ID {material_id}.")
            return False # Nenhuma linha foi afetada
        
    except (Exception, psycopg2.DatabaseError) as error:
        # Se este material estiver sendo usado (ex: FK em outra tabela),
        # o banco de dados dará um erro aqui, protegendo a integridade.
        print(f"Model Error (Estoque): Erro ao deletar material: {error}")
        if conn:
            conn.rollback() # Desfaz a transação
        return False
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            release_connection(conn)

def update_material_estoque(material_id, nova_quantidade):
    """
    Atualiza APENAS a coluna 'estoque_atual' de um material.
    Usado para dar baixa ou estornar (retornar) estoque.
    """
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        query = """
        UPDATE materiais SET
            estoque_atual = %s,
            data_atualizacao = CURRENT_TIMESTAMP
        WHERE
            id = %s;
        """
        
        cursor.execute(query, (nova_quantidade, material_id))
        conn.commit()
        
        if cursor.rowcount > 0:
            print(f"Model (Estoque): Estoque do ID {material_id} atualizado para {nova_quantidade}.")
            return True
        else:
            print(f"Model (Estoque): Erro ao atualizar estoque. ID {material_id} não encontrado.")
            return False

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Erro ao atualizar estoque do material: {error}")
        if conn:
            conn.rollback()
        return False
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            release_connection(conn)
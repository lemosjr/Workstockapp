from app.utils.db_connector import get_connection, release_connection
import psycopg2
from psycopg2 import extras # Para retornar dicts

"""
Camada Model (Modelo) para Usuários.

Responsabilidade:
- Funções para buscar dados de usuários no banco.
"""

def create_user(nome, email, senha_hash, perfil):
    """
    Cria um novo usuário no banco de dados.
    Recebe a senha JÁ HASHEADA do controller.
    """
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        query = """
        INSERT INTO usuarios (nome_completo, email, senha_hash, perfil)
        VALUES (%s, %s, %s, %s)
        RETURNING id;
        """
        
        # O psycopg2 faz a limpeza (sanitize) dos dados
        cursor.execute(query, (nome, email, senha_hash, perfil))
        
        new_id = cursor.fetchone()[0]
        conn.commit() # Confirma a transação
        
        print(f"Model: Novo usuário criado com sucesso. ID: {new_id}")
        return new_id
        
    except psycopg2.IntegrityError as e:
        # Erro especial do PostgreSQL para 'UNIQUE constraint' (email duplicado)
        print(f"Model Error (IntegrityError): Email provavelmente duplicado. {e}")
        if conn:
            conn.rollback() # Desfaz a transação
        return None
        
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Model Error: Erro ao criar usuário: {error}")
        if conn:
            conn.rollback()
        return None
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            release_connection(conn)

def get_user_by_email(email):
    """
    Busca um usuário específico pelo seu email.
    O email é UNIQUE, então deve retornar 0 ou 1 usuário.
    Retorna um dicionário (DictRow) com os dados do usuário.
    """
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=extras.DictCursor)
        
        query = "SELECT * FROM usuarios WHERE email = %s AND ativo = TRUE;"
        cursor.execute(query, (email,))
        
        user_data = cursor.fetchone() # Pega apenas um resultado
        return user_data
        
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Erro ao buscar usuário por email ({email}): {error}")
        return None
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            release_connection(conn)

# (Futuramente, adicionaríamos: create_user, update_user, deactivate_user, etc.)
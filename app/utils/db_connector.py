import psycopg2
from psycopg2 import pool
from config import settings  # Importamos nossas configurações
import sys

# Variável global para armazenar o pool de conexões
_connection_pool = None

def init_db_pool():
    """
    Inicializa o pool de conexões com o PostgreSQL.
    Esta função DEVE ser chamada na inicialização do app (em main.py).
    """
    global _connection_pool
    if _connection_pool:
        return  # Já inicializado

    try:
        print("Inicializando pool de conexões com o PostgreSQL...")
        _connection_pool = psycopg2.pool.SimpleConnectionPool(
            minconn=1,   # Mínimo de conexões prontas
            maxconn=10,  # Máximo de conexões que o pool pode criar
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            database=settings.DB_NAME
        )
        print("Pool de conexões inicializado com sucesso.")
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Erro ao inicializar o pool de conexões: {error}")
        sys.exit(1) # Falha crítica: se não conectar ao DB, a app não pode funcionar

def get_connection():
    """
    Obtém uma conexão do pool.
    
    Importante: Sempre que obter uma conexão, você DEVE
    liberá-la usando release_connection() quando terminar.
    """
    if _connection_pool is None:
        print("Erro: O pool de conexões não foi inicializado.")
        init_db_pool() # Tenta inicializar
    
    try:
        # Pega uma conexão "pronta" da garagem
        conn = _connection_pool.getconn()
        return conn
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Erro ao obter conexão do pool: {error}")
        return None

def release_connection(conn):
    """
    Devolve uma conexão ao pool para que outros possam usá-la.
    """
    if _connection_pool:
        try:
            # Devolve o "carro" para a garagem
            _connection_pool.putconn(conn)
        except (Exception, psycopg2.DatabaseError) as error:
            print(f"Erro ao devolver conexão ao pool: {error}")

def close_db_pool():
    """
    Fecha todas as conexões no pool.
    Esta função DEVE ser chamada ao fechar o app (em main.py).
    """
    global _connection_pool
    if _connection_pool:
        _connection_pool.closeall()
        _connection_pool = None
        print("Pool de conexões fechado.")
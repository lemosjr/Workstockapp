import os
from dotenv import load_dotenv

# Encontra o caminho para o arquivo .env (que está na raiz do projeto)
# __file__ é o caminho deste arquivo (settings.py)
# os.path.dirname() sobe um nível (para /config)
# os.path.dirname() sobe outro nível (para a raiz /workstockapp)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(BASE_DIR, '.env')

# Carrega as variáveis do arquivo .env para o ambiente do sistema
load_dotenv(dotenv_path=ENV_PATH)

# --- Configurações do Banco de Dados ---
# Usamos os.getenv() para ler as variáveis carregadas
# O segundo parâmetro (ex: "localhost") é um valor padrão caso a variável não exista no .env
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "workstock_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD") # Deixamos None se não for encontrado
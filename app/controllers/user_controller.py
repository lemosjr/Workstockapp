from app.models import usuario_model
import bcrypt # Para criar o hash da senha
import re # Para validar o e-mail (Regex)

"""
Camada Controller (Controlador) para Gerenciamento de Usuários.

Responsabilidade:
- Orquestrar a lógica de negócio de criação de usuários.
- Validar dados (campos, senhas, e-mail duplicado).
- Criar o HASH seguro da senha (bcrypt).
- Chamar o Model para salvar o usuário.
"""

# Lista de perfis válidos (baseado no ENUM do DB)
VALID_PROFILES = ['empresa', 'proprietario', 'cliente']

# Expressão regular simples para validar e-mail
EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'


def register_user(data):
    """
    Controlador para registrar um novo usuário.
    'data' é um dicionário vindo da View contendo:
    'nome', 'email', 'senha', 'confirma_senha', 'perfil'
    """
    
    nome = data.get('nome', '').strip()
    email = data.get('email', '').strip().lower()
    senha = data.get('senha', '')
    confirma_senha = data.get('confirma_senha', '')
    perfil = data.get('perfil', '').lower()

    # --- 1. Lógica de Negócio e Validação ---

    # Validação de campos vazios
    if not nome or not email or not senha or not confirma_senha or not perfil:
        print("Controller (User): Erro: Todos os campos são obrigatórios.")
        return (False, "Erro: Todos os campos são obrigatórios.")

    # Validação de e-mail (formato)
    if not re.match(EMAIL_REGEX, email):
        print("Controller (User): Erro: Formato de e-mail inválido.")
        return (False, "Erro: Formato de e-mail inválido.")

    # Validação de senhas
    if senha != confirma_senha:
        print("Controller (User): Erro: As senhas não coincidem.")
        return (False, "Erro: As senhas não coincidem.")
        
    if len(senha) < 6:
        print("Controller (User): Erro: A senha deve ter pelo menos 6 caracteres.")
        return (False, "Erro: A senha deve ter pelo menos 6 caracteres.")

    # Validação do perfil
    if perfil not in VALID_PROFILES:
        print(f"Controller (User): Erro: Perfil '{perfil}' inválido.")
        return (False, "Erro: Perfil de usuário inválido.")
        
    # --- 2. Verificação de Duplicidade (Model) ---
    
    print(f"Controller (User): Verificando se o e-mail '{email}' já existe...")
    existing_user = usuario_model.get_user_by_email(email)
    
    if existing_user:
        print("Controller (User): Erro: E-mail já cadastrado.")
        return (False, "Erro: Este e-mail já está em uso.")

    # --- 3. Hashing da Senha (Segurança) ---
    
    try:
        print("Controller (User): Gerando hash da senha...")
        senha_bytes = senha.encode('utf-8')
        
        # Gera o "sal" e cria o hash
        senha_hash = bcrypt.hashpw(senha_bytes, bcrypt.gensalt())
        
        # Converte o hash (bytes) de volta para string para salvar no DB
        senha_hash_str = senha_hash.decode('utf-8')
        
        print("Controller (User): Hash gerado com sucesso.")

    except Exception as e:
        print(f"Controller (User): Erro crítico ao gerar hash: {e}")
        return (False, "Erro interno ao processar senha. Tente novamente.")

    # --- 4. Chamada ao Model (Create) ---
    
    print(f"Controller (User): Enviando dados para o Model criar o usuário {email}...")
    
    novo_id = usuario_model.create_user(
        nome=nome, 
        email=email, 
        senha_hash=senha_hash_str, 
        perfil=perfil
    )

    # --- 5. Resposta para a View ---
    
    if novo_id:
        msg = f"Usuário '{nome}' (Perfil: {perfil}) criado com sucesso!"
        return (True, msg)
    else:
        # A única falha aqui seria o IntegrityError (e-mail duplicado)
        # que já checamos, mas é bom ter como fallback.
        return (False, "Erro ao salvar usuário no banco de dados. (E-mail duplicado?)")
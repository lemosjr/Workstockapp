from app.models import usuario_model
import bcrypt # Importamos a biblioteca de hashing

"""
Camada Controller (Controlador) para Autenticação.

Responsabilidade:
- Orquestrar a lógica de negócio de Login.
- Validar entradas do usuário (email, senha).
- Usar bcrypt para comparar senhas de forma segura.
- Retornar o status do login para a View.
"""

def login(email, senha):
    """
    Controlador para tentar realizar o login.
    Recebe email e senha (texto puro) da View.
    """
    
    # --- 1. Validação de Lógica de Negócio ---
    
    if not email or not senha:
        print("Controller (Auth): Tentativa de login com campos vazios.")
        return (False, "E-mail e Senha são obrigatórios.")

    # --- 2. Chamada ao Model ---
    
    print(f"Controller (Auth): Buscando usuário '{email}' no Model.")
    # Busca o usuário no banco de dados
    user_data = usuario_model.get_user_by_email(email)
    
    # --- 3. Verificação de Segurança (Hashing) ---
    
    # Se o usuário não foi encontrado (ou está inativo)
    if not user_data:
        print(f"Controller (Auth): Falha no login. Usuário não encontrado ou inativo: {email}")
        # MENSAGEM GENÉRICA: Por segurança, não diga "Usuário não existe".
        return (False, "E-mail ou senha inválidos.")

    # --- O Ponto Principal: Comparando Senhas com BCRYPT ---
    
    try:
        # Pega a senha em texto puro e transforma em bytes
        senha_bytes = senha.strip().encode('utf-8')
        
        # Pega o hash salvo no banco e transforma em bytes
        hash_bytes = user_data['senha_hash'].strip().encode('utf-8')
        
        # O Bcrypt compara o hash da senha digitada com o hash do banco
        is_valid = bcrypt.checkpw(senha_bytes, hash_bytes)
        
        if is_valid:
            print(f"Controller (Auth): Login bem-sucedido para {email}.")
            # Login OK. Retornamos os dados do usuário para a "sessão"
            user_info = {
                "id": user_data['id'],
                "nome": user_data['nome_completo'],
                "email": user_data['email'],
                "perfil": user_data['perfil'] # Ex: 'empresa', 'proprietario'
            }
            # (Sucesso, Dados do Usuário)
            return (True, user_info)
        else:
            # A senha estava errada
            print(f"Controller (Auth): Falha no login. Senha incorreta para {email}.")
            return (False, "E-mail ou senha inválidos.")
            
    except Exception as e:
        print(f"Controller (Auth): Erro crítico durante verificação de senha. {e}")
        return (False, "Ocorreu um erro no sistema. Tente novamente.")
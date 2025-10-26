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
        # --- DEBUG: Vamos verificar os valores ---
        print("\n--- INICIANDO DEBUG BCRYPT ---")

        print(f"Senha (texto puro) recebida: '{senha}'")
        senha_bytes = senha.encode('utf-8')
        print(f"Senha (bytes) para comparar: {senha_bytes}")

        hash_do_banco = user_data['senha_hash']
        print(f"Hash (string) vindo do DB: '{hash_do_banco}'")
        hash_bytes = hash_do_banco.encode('utf-8')
        print(f"Hash (bytes) para comparar: {hash_bytes}")

        hash_correto_conhecido = '$2b$12$DWO.0.Nb.j/5585.i08.GON.GV0G2.d.m.3o/fiosXg9Oq9o.3pXG'
        print(f"Hash (correto) esperado:   '{hash_correto_conhecido}'")

        # Vamos verificar se a string do banco tem espaços ou é diferente
        if hash_do_banco == hash_correto_conhecido:
            print("Verificação (String): Hash do banco É IGUAL ao esperado.")
        else:
            print("Verificação (String): !!! ATENÇÃO !!! HASH DO BANCO É DIFERENTE DO ESPERADO!")
            print(f"Comprimento do Hash do DB: {len(hash_do_banco)}")
            print(f"Comprimento do Hash Esperado: {len(hash_correto_conhecido)}")

        print("--- FIM DEBUG BCRYPT ---\n")
        # --- FIM DEBUG ---

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
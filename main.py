from app.views.main_view import MainView
from app.views.login_view import LoginView 
from app.utils import db_connector
import sys
import customtkinter as ctk

"""
Ponto de Entrada Principal (Entry Point) da Aplicação WorkStock.

Responsabilidades:
1. Inicializar serviços essenciais (DB Pool).
2. Chamar a Tela de Login (LoginView).
3. Aguardar o resultado do login.
4. Se o login for bem-sucedido, chamar a Tela Principal (MainView).
5. Gerenciar o desligamento limpo.
"""

def main():
    # --- 1. Inicialização ---
    print("Iniciando aplicação WorkStock...")
    try:
        # Inicializa o pool de conexões ANTES de qualquer tela
        db_connector.init_db_pool()
    except Exception as e:
        print(f"CRÍTICO: Falha ao inicializar a conexão com o banco de dados: {e}")
        sys.exit(1) # Sai do app se não puder conectar

    # Configurações globais do CustomTkinter
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")
    
    # --- 2. Exibição da Tela de Login ---
    login_app = LoginView()
    # A linha abaixo "pausa" o script aqui até a janela de login fechar
    login_app.mainloop() 
    
    # --- 3. Verificação do Resultado do Login ---
    # O script continua daqui quando a LoginView é fechada
    
    if login_app.login_successful:
        print("Login bem-sucedido. Iniciando a aplicação principal...")
        
        # Pega os dados do usuário que logou
        user_data = login_app.user_data 
        
        # --- 4. Exibição da Tela Principal (MainView) ---
        try:
            # Passamos os dados do usuário para a MainView
            main_app = MainView(user_data=user_data) 
            
            # Gerenciamento de desligamento da janela principal
            main_app.protocol("WM_DELETE_WINDOW", lambda: on_closing(main_app))
            main_app.mainloop()
            
        except Exception as e:
            print(f"Erro inesperado na aplicação principal: {e}")
    else:
        print("Login falhou ou foi cancelado. Encerrando aplicação.")

    # --- 5. Desligamento Limpo ---
    # (Só será chamado após a MainView ou LoginView fechar)
    db_connector.close_db_pool()
    print("App finalizado.")

def on_closing(app):
    """
    Função chamada quando o usuário fecha a janela principal (MainView).
    """
    print("Fechando aplicação...")
    # (O pool será fechado no bloco 'finally' do main.py)
    app.destroy()

if __name__ == "__main__":
    main()
# CÓDIGO RESTAURADO (VERSÃO FINAL)
from app.views.main_view import MainView
from app.views.login_view import LoginView 
from app.utils import db_connector
import sys
import customtkinter as ctk

def main():
    print("Iniciando aplicação WorkStock...")
    try:
        db_connector.init_db_pool()
    except Exception as e:
        print(f"CRÍTICO: Falha ao inicializar a conexão com o banco de dados: {e}")
        sys.exit(1)

    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")

    login_app = LoginView()
    login_app.mainloop() 

    if login_app.login_successful:
        print("Login bem-sucedido. Iniciando a aplicação principal...")
        user_data = login_app.user_data 

        try:
            main_app = MainView(user_data=user_data) 
            main_app.protocol("WM_DELETE_WINDOW", lambda: on_closing(main_app))
            main_app.mainloop()

        except Exception as e:
            print(f"Erro inesperado na aplicação principal: {e}")
    else:
        print("Login falhou ou foi cancelado. Encerrando aplicação.")

    db_connector.close_db_pool()
    print("App finalizado.")

def on_closing(app):
    print("Fechando aplicação...")
    app.destroy()

if __name__ == "__main__":
    main()
from app.views.main_view import MainView
from app.utils import db_connector
import sys

"""
Ponto de Entrada Principal (Entry Point) da Aplicação WorkStock.

Responsabilidades:
1. Inicializar serviços essenciais (ex: Pool de Conexão com DB).
2. Instanciar e exibir a View Principal (MainView).
3. Iniciar o loop principal da aplicação (mainloop).
4. Gerenciar o desligamento limpo (ex: fechar o pool do DB).
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

    # --- 2. Criação da View Principal ---
    try:
        app = MainView()
        
        # --- 4. Gerenciamento de Desligamento ---
        # Intercepta o clique no "X" da janela
        app.protocol("WM_DELETE_WINDOW", lambda: on_closing(app))
        
        # --- 3. Início do Loop Principal ---
        app.mainloop()
        
    except Exception as e:
        print(f"Erro inesperado na aplicação: {e}")
    finally:
        # Garante que o pool seja fechado, não importa como o app saiu
        print("App finalizado.")
        

def on_closing(app):
    """
    Função chamada quando o usuário fecha a janela principal.
    """
    print("Fechando aplicação...")
    # Fecha o pool de conexões do banco de dados
    db_connector.close_db_pool()
    # Destrói a janela da aplicação
    app.destroy()

if __name__ == "__main__":
    main()
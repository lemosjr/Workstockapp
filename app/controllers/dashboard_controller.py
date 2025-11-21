from app.models import os_model
from app.models import estoque_model

"""
Camada Controller para o Dashboard.
Agrega dados de múltiplos models.
"""

def get_dashboard_data():
    """
    Coleta todas as métricas necessárias para o Dashboard.
    """
    print("Controller (Dash): Coletando métricas...")
    
    # Busca dados de OS
    os_stats = os_model.get_os_stats()
    
    # Busca dados de Estoque
    estoque_baixo = estoque_model.get_estoque_baixo_count()
    
    # Monta o objeto final
    data = {
        "os_abertas": os_stats["total_abertas"],
        "os_andamento": os_stats["total_em_andamento"],
        "os_pendentes": os_stats["total_pendentes"],
        "faturamento": os_stats["valor_em_projetos"],
        "alertas_estoque": estoque_baixo
    }
    
    return (True, data)
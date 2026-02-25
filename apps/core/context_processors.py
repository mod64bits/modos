from .models import ConfiguracaoGeral

def system_config(request):
    """
    Disponibiliza a variável {{ config }} em todos os templates HTML.
    Isso evita ter que buscar no banco de dados em cada View.
    """
    return {
        'system_config': ConfiguracaoGeral.load()
    }
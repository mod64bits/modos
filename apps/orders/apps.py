from django.apps import AppConfig


class OrdersConfig(AppConfig):
    name = 'apps.orders'
    verbose_name = 'Gestão de O.S. e Chamados'
    def ready(self):
        # CORREÇÃO CRÍTICA: Importa os signals quando o Django inicia.
        # Sem esta linha, os logs de email NUNCA são criados e o Celery não é acionado!
        import apps.orders.signals

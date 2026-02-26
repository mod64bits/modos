from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = 'apps.core'

    def ready(self):
        # Esta linha faz com que o Django carregue o arquivo de disparos (signals)
        # assim que o servidor iniciar.
        import apps.orders.signals

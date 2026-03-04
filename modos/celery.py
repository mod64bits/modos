import os
from celery import Celery

# Define o módulo de definições padrão do Django para o Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'modos.settings')

# Cria a instância da aplicação Celery
app = Celery('modos')

# Usa uma string para que o worker não tenha de serializar o objeto de configuração.
# namespace='CELERY' significa que as configs no settings.py devem começar por CELERY_
app.config_from_object('django.conf:settings', namespace='CELERY')

# Procura tarefas automaticamente nos ficheiros tasks.py de todos os INSTALLED_APPS
app.autodiscover_tasks()

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
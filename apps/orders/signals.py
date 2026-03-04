from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Chamado
from .tasks import enviar_email_chamado_task

@receiver(post_save, sender=Chamado)
def notificar_atualizacao_chamado(sender, instance, created, **kwargs):
    """
    Signal ativado pelo Django ao salvar um Chamado.
    Em vez de processar o envio na thread atual, atiramos o ID para a fila do Redis.
    """
    # Usamos o .delay() do Celery. Retorna a página instantaneamente para o utilizador!
    enviar_email_chamado_task.delay(instance.id, created)
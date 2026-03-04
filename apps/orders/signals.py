import logging
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Chamado, LogEmail
from .tasks import enviar_email_chamado_task

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Chamado)
def notificar_atualizacao_chamado(sender, instance, created, **kwargs):
    """
    Signal ativado pelo Django ao salvar um Chamado.
    Cria o Log na base de dados e envia para a fila do Celery de forma segura.
    """
    assunto = f"[TI Manager] {'Novo Chamado Aberto' if created else 'Atualização no Chamado'}: #{instance.numero}"
    
    # 1. Cria o registo de log na base de dados imediatamente
    log_email = LogEmail.objects.create(
        chamado=instance,
        assunto=assunto,
        status='PENDENTE'
    )
    
    # 2. Atira a tarefa para o Celery (Redis) APENAS quando a transação for guardada
    # Isso evita que o Celery tente ler um log que ainda não terminou de ser gravado!
    transaction.on_commit(
        lambda: enviar_email_chamado_task.delay(instance.id, created, log_email.id)
    )
    
    logger.info(f"Signal disparado com sucesso para o chamado #{instance.numero}. Log ID: {log_email.id}")
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

@shared_task
def enviar_email_chamado_task(chamado_id, created):
    """
    Tarefa assíncrona gerida pelo Celery para disparar e-mails.
    Lógica adaptada para respeitar o isolamento Multi-tenant do Django.
    """
    from apps.orders.models import Chamado
    from apps.accounts.models import Usuario
    
    # Tentamos importar as configurações dinâmicas de email/site
    try:
        from apps.core.models import ConfiguracaoEmail, ConfiguracaoGeral
    except ImportError:
        ConfiguracaoEmail = None
        ConfiguracaoGeral = None

    # Otimização Django: Usa select_related para evitar múltiplas queries (N+1)
    try:
        instance = Chamado.objects.select_related('solicitante', 'tecnico_atribuido', 'empresa').get(id=chamado_id)
    except Chamado.DoesNotExist:
        logger.warning(f"Chamado {chamado_id} não encontrado para envio de e-mail.")
        return

    # 1. Carregar configurações
    remetente = getattr(settings, 'DEFAULT_FROM_EMAIL', 'nao-responda@seusistema.com')
    dominio_sistema = getattr(settings, 'SITE_URL', 'http://172.16.254.77:8000')

    if ConfiguracaoEmail:
        try:
            config_email = ConfiguracaoEmail.load()
            remetente = config_email.email_remetente or remetente
        except Exception:
            pass

    if ConfiguracaoGeral:
        try:
            config_geral = ConfiguracaoGeral.load()
            dominio_sistema = config_geral.site_url.rstrip('/') or dominio_sistema
        except Exception:
            pass

    # 2. Definir Destinatários (Usamos set() para evitar e-mails duplicados)
    destinatarios = set()
    
    # 2.1 Adiciona o Solicitante
    if instance.solicitante and instance.solicitante.email:
        destinatarios.add(instance.solicitante.email)

    # 2.2 Lógica Multi-tenant para Técnicos e Admins
    # Puxa todos os usuários ativos com permissão de Staff e email preenchido
    admins_tecnicos = Usuario.objects.filter(
        is_staff=True, 
        is_active=True
    ).exclude(email__isnull=True).exclude(email="")

    for admin in admins_tecnicos:
        # Se for superusuário do sistema inteiro, ou pertencer à mesma empresa do chamado
        if admin.is_superuser or (instance.empresa and admin.empresa == instance.empresa):
            destinatarios.add(admin.email)

    # 2.3 Adiciona o Técnico Atribuído especificamente (Garantia extra)
    if instance.tecnico_atribuido and instance.tecnico_atribuido.email:
        destinatarios.add(instance.tecnico_atribuido.email)

    if not destinatarios:
        return

    # 3. Montar o E-mail
    if created:
        assunto = f"[TI Manager] Novo Chamado Aberto: #{instance.numero}"
        texto_intro = "Um novo chamado foi aberto com sucesso no sistema e encaminhado para a equipe técnica."
    else:
        assunto = f"[TI Manager] Atualização no Chamado: #{instance.numero}"
        texto_intro = "Ocorreu uma atualização, comentário ou alteração de status no chamado."

    link_chamado = f"{dominio_sistema}/orders/{instance.id}/"

    mensagem = f"""Olá,

{texto_intro}

DETALHES DA O.S.
--------------------------------------------------
Protocolo: #{instance.numero}
Assunto: {instance.titulo}
Status: {instance.get_status_display()}
Prioridade: {instance.get_prioridade_display()}
Técnico: {instance.tecnico_atribuido.get_full_name() if instance.tecnico_atribuido else "Aguardando Atribuição"}

Para visualizar o histórico, adicionar novos comentários ou acompanhar o laudo técnico, clique no link abaixo:
{link_chamado}

--------------------------------------------------
Este é um e-mail automático do sistema de Gestão de TI. Por favor, não responda.
"""

    # 4. Disparo Efetivo
    send_mail(
        subject=assunto,
        message=mensagem,
        from_email=remetente,
        recipient_list=list(destinatarios),
        fail_silently=True,
    )
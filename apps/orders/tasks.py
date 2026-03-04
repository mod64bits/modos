from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


@shared_task
def enviar_email_chamado_task(chamado_id, created, log_id):
    """
    Tarefa assíncrona gerida pelo Celery para disparar e-mails.
    Atualiza o LogEmail com o status de sucesso ou erro.
    """
    from apps.orders.models import Chamado, LogEmail
    from apps.accounts.models import Usuario

    try:
        from apps.core.models import ConfiguracaoEmail, ConfiguracaoGeral
    except ImportError:
        ConfiguracaoEmail = None
        ConfiguracaoGeral = None

    # Resgata o log que foi criado no Signal
    try:
        log_email = LogEmail.objects.get(id=log_id)
    except LogEmail.DoesNotExist:
        logger.warning(f"Log de email {log_id} não encontrado na base de dados.")
        return

    try:
        instance = Chamado.objects.select_related(
            "solicitante", "tecnico_atribuido", "empresa"
        ).get(id=chamado_id)
    except Chamado.DoesNotExist:
        log_email.status = "ERRO"
        log_email.erro_mensagem = "O Chamado foi apagado antes do e-mail ser enviado."
        log_email.save()
        return

    # 1. Carregar configurações
    remetente = getattr(settings, "DEFAULT_FROM_EMAIL", "nao-responda@seusistema.com")
    dominio_sistema = getattr(settings, "SITE_URL", "http://localhost:8000")

    if ConfiguracaoEmail:
        try:
            config_email = ConfiguracaoEmail.load()
            remetente = config_email.email_remetente or remetente
        except Exception:
            pass

    if ConfiguracaoGeral:
        try:
            config_geral = ConfiguracaoGeral.load()
            dominio_sistema = config_geral.site_url.rstrip("/") or dominio_sistema
        except Exception:
            pass

    # 2. Definir Destinatários
    destinatarios = set()

    if instance.solicitante and instance.solicitante.email:
        destinatarios.add(instance.solicitante.email)

    admins_tecnicos = (
        Usuario.objects.filter(is_staff=True, is_active=True)
        .exclude(email__isnull=True)
        .exclude(email="")
    )

    for admin in admins_tecnicos:
        if admin.is_superuser or (
            instance.empresa and admin.empresa == instance.empresa
        ):
            destinatarios.add(admin.email)

    if instance.tecnico_atribuido and instance.tecnico_atribuido.email:
        destinatarios.add(instance.tecnico_atribuido.email)

    # Se não houver destinatários, aborta e atualiza o log
    if not destinatarios:
        log_email.status = "ERRO"
        log_email.erro_mensagem = (
            "Nenhum destinatário válido encontrado (utilizadores sem e-mail registado)."
        )
        log_email.save()
        return

    # Atualiza o log com os destinatários que vão receber
    log_email.destinatarios = ", ".join(list(destinatarios))
    log_email.save()

    # 3. Montar o E-mail
    if created:
        texto_intro = "Um novo chamado foi aberto com sucesso no sistema e encaminhado para a equipa técnica."
    else:
        texto_intro = (
            "Ocorreu uma atualização, comentário ou alteração de status no chamado."
        )

    link_chamado = f"{dominio_sistema}/orders/{instance.id}/"
    tecnico_nome = (
        instance.tecnico_atribuido.get_full_name()
        if instance.tecnico_atribuido
        else "Aguardando Atribuição"
    )

    mensagem = f"""Olá,

{texto_intro}

DETALHES DA O.S.
--------------------------------------------------
Protocolo: #{instance.numero}
Assunto: {instance.titulo}
Status: {instance.get_status_display()}
Prioridade: {instance.get_prioridade_display()}
Técnico: {tecnico_nome}

Para visualizar o histórico ou acompanhar o laudo técnico, clique no link abaixo:
{link_chamado}

--------------------------------------------------
Este é um e-mail automático do sistema de Gestão de TI. Por favor, não responda.
"""

    # 4. Disparo Efetivo com Captura de Erro
    try:
        send_mail(
            subject=log_email.assunto,
            message=mensagem,
            from_email=remetente,
            recipient_list=list(destinatarios),
            fail_silently=False,
        )

        # Se chegou aqui, enviou com sucesso
        log_email.status = "ENVIADO"
        log_email.save()

    except Exception as e:
        logger.error(f"Erro ao enviar email do chamado {instance.numero}: {e}")
        log_email.status = "ERRO"
        log_email.erro_mensagem = str(e)
        log_email.save()

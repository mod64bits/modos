from celery import shared_task
from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from django.utils import timezone
import logging
from .models import Chamado
from apps.core.gerador_pdf import render_to_pdf

logger = logging.getLogger(__name__)


@shared_task
def enviar_email_chamado_task(chamado_id, created, log_id):
    """
    Tarefa assíncrona padrão para avisos de criação/atualização de chamados.
    """
    from apps.orders.models import Chamado, LogEmail

    try:
        from apps.accounts.models import Usuario
    except ImportError:
        from accounts.models import Usuario

    try:
        from apps.core.models import ConfiguracaoEmail, ConfiguracaoGeral
    except ImportError:
        ConfiguracaoEmail = None
        ConfiguracaoGeral = None

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

    remetente = getattr(settings, "DEFAULT_FROM_EMAIL", "nao-responda@seusistema.com")
    dominio_sistema = getattr(settings, "SITE_URL", "http://localhost:8000")

    if ConfiguracaoEmail:
        try:
            config_email = ConfiguracaoEmail.load()
            remetente = config_email.email_remetente or remetentedocker
        except Exception:
            pass

    if ConfiguracaoGeral:
        try:
            config_geral = ConfiguracaoGeral.load()
            dominio_sistema = config_geral.site_url.rstrip("/") or dominio_sistema
        except Exception:
            pass

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

    if not destinatarios:
        log_email.status = "ERRO"
        log_email.erro_mensagem = "Nenhum destinatário válido encontrado."
        log_email.save()
        return

    log_email.destinatarios = ", ".join(list(destinatarios))
    log_email.save()

    texto_intro = (
        "Um novo chamado foi aberto com sucesso no sistema e encaminhado para a equipa técnica."
        if created
        else "Ocorreu uma atualização, comentário ou alteração de status no chamado."
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

    try:
        send_mail(
            subject=log_email.assunto,
            message=mensagem,
            from_email=remetente,
            recipient_list=list(destinatarios),
            fail_silently=False,
        )
        log_email.status = "ENVIADO"
        log_email.save()
    except Exception as e:
        logger.error(f"Erro ao enviar email do chamado {instance.numero}: {e}")
        log_email.status = "ERRO"
        log_email.erro_mensagem = str(e)
        log_email.save()


# ==========================================
# NOVA TAREFA: Geração e Envio de PDF
# ==========================================


@shared_task
def enviar_pdf_chamado_email_task(chamado_id):
    """
    Gera o PDF do chamado em memória e envia anexado por e-mail para o cliente.
    """

    try:
        chamado = Chamado.objects.select_related(
            "solicitante", "tecnico_atribuido", "empresa"
        ).get(id=chamado_id)
    except Chamado.DoesNotExist:
        return

    context = {
        "chamado": chamado,
        "comentarios": chamado.comentarios.all(),
        "gerado_por": "Sistema (Envio Técnico)",
        "data_geracao": timezone.now(),
    }

    # 1. Gera o PDF usando o nosso conversor em memória (Não grava no HD)
    pdf_response = render_to_pdf("orders/chamado_pdf.html", context)

    if not pdf_response:
        logger.error(f"Falha ao gerar o PDF para anexo da O.S. #{chamado.numero}.")
        return

    # 2. Prepara o destinatário (O Solicitante do Chamado)
    destinatarios = set()
    if chamado.solicitante and chamado.solicitante.email:
        destinatarios.add(chamado.solicitante.email)

    if not destinatarios:
        logger.warning(
            f"O solicitante da O.S. #{chamado.numero} não possui e-mail registrado."
        )
        return

    # 3. Carrega configurações do remetente
    remetente = getattr(settings, "DEFAULT_FROM_EMAIL", "nao-responda@seusistema.com")
    try:
        from apps.core.models import ConfiguracaoEmail

        config_email = ConfiguracaoEmail.load()
        remetente = config_email.email_remetente or remetente
    except Exception:
        pass

    assunto = f"Laudo Técnico da O.S. #{chamado.numero} - {chamado.titulo}"
    mensagem = f"Olá {chamado.solicitante.first_name},\n\nConforme solicitado, segue em anexo o laudo técnico em PDF do atendimento referente à O.S. #{chamado.numero}.\n\nCumprimentos,\nEquipe de TI."

    # 4. Cria o objeto EmailMessage (Necessário para adicionar anexos)
    email = EmailMessage(
        subject=assunto,
        body=mensagem,
        from_email=remetente,
        to=list(destinatarios),
    )

    # Anexa o binário do PDF ao email
    email.attach(f"OS_{chamado.numero}.pdf", pdf_response, "application/pdf")

    try:
        email.send()
        logger.info(
            f"PDF da O.S. #{chamado.numero} enviado com sucesso para {destinatarios}."
        )
    except Exception as e:
        logger.error(f"Erro ao disparar PDF por e-mail: {e}")

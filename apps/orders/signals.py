from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from apps.orders.models import Chamado

@receiver(post_save, sender=Chamado)
def notificar_atualizacao_chamado(sender, instance, created, **kwargs):
    # A importação dos modelos do core deve ficar DENTRO da função 
    # para evitar falhas silenciosas de carregamento prematuro (AppRegistryNotReady)
    from apps.core.models import ConfiguracaoEmail, ConfiguracaoGeral
    
    # 1. Carregar as configurações de remetente do Banco de Dados
    try:
        config_email = ConfiguracaoEmail.load()
        remetente = config_email.email_remetente
    except Exception as e:
        print(f"Erro ao carregar remetente: {e}")
        remetente = getattr(settings, 'DEFAULT_FROM_EMAIL', 'nao-responda@seusistema.com')

    # 2. Definir destinatários
    destinatarios = set()
    if instance.solicitante and instance.solicitante.email:
        destinatarios.add(instance.solicitante.email)
    
    if instance.tecnico_atribuido and instance.tecnico_atribuido.email:
        destinatarios.add(instance.tecnico_atribuido.email)

    if not destinatarios:
        return

    # 3. Montar o Assunto e a Introdução
    if created:
        assunto = f"[TI Manager] Novo Chamado Aberto: #{instance.numero}"
        texto_intro = "Um novo chamado foi aberto com sucesso no sistema e está aguardando atendimento."
    else:
        assunto = f"[TI Manager] Atualização no Chamado: #{instance.numero}"
        texto_intro = "Ocorreu uma atualização ou alteração de status no seu chamado."

    # 4. Gerar o link do chamado pegando a URL correta do Banco de Dados
    try:
        config_geral = ConfiguracaoGeral.load()
        dominio_sistema = config_geral.site_url.rstrip('/')
    except Exception as e:
        print(f"Erro ao carregar URL da base de dados: {e}")
        # Fallback de segurança apenas se der erro crítico no banco de dados
        dominio_sistema = 'http://172.16.254.77:8000'
        
    link_chamado = f"{dominio_sistema}/orders/{instance.id}/"

    # 5. Montar o Corpo do E-mail
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

    # 6. Realizar o envio
    send_mail(
        subject=assunto,
        message=mensagem,
        from_email=remetente,
        recipient_list=list(destinatarios),
        fail_silently=True,
    )
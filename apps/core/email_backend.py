from django.core.mail.backends.smtp import EmailBackend
from django.db.utils import OperationalError, ProgrammingError

class ConfiguracaoDBEmailBackend(EmailBackend):
    """
    Backend de E-mail Customizado.
    Sempre que o Django tenta enviar um e-mail (usando send_mail), 
    ele passa por aqui, procura as configurações no Banco de Dados 
    e substitui as credenciais padrão do settings.py.
    """
    def __init__(self, fail_silently=False, **kwargs):
        super().__init__(fail_silently=fail_silently, **kwargs)
        
        # Fazemos a importação aqui dentro para evitar problemas de carregamento circular
        from .models import ConfiguracaoEmail
        
        try:
            config = ConfiguracaoEmail.objects.get(pk=1)
            # Sobrescreve as configurações do Django com as do Banco de Dados
            self.host = config.servidor_smtp or self.host
            self.port = config.porta or self.port
            self.username = config.usuario or self.username
            self.password = config.senha or self.password
            self.use_tls = config.usar_tls
            self.use_ssl = config.usar_ssl
        except (ConfiguracaoEmail.DoesNotExist, OperationalError, ProgrammingError):
            # Fallback: Se a tabela não existir (ex: durante a primeira migração) 
            # ou não houver registo, não quebra a aplicação.
            pass
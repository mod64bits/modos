from django.db import models

class ConfiguracaoGeral(models.Model):
    """
    Modelo Singleton para armazenar configurações globais do sistema.
    Só permite um registro no banco de dados.
    """
    titulo_sistema = models.CharField(
        "Título do Sistema (Header)", 
        max_length=100, 
        default="TI Manager",
        help_text="Texto que aparece na barra superior (Navbar)."
    )
    
    texto_rodape = models.CharField(
        "Texto do Rodapé", 
        max_length=255, 
        default="Sistema de Gestão de TI. Todos os direitos reservados.",
        help_text="Texto de copyright que aparece no final da página."
    )
    
    # Singleton: Forçamos o ID a ser sempre 1
    def save(self, *args, **kwargs):
        self.pk = 1
        super(ConfiguracaoGeral, self).save(*args, **kwargs)

    # Impede a exclusão do registro para não quebrar o layout
    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls):
        """Método helper para carregar a config ou criar a padrão se não existir"""
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return "Configurações do Sistema"

    class Meta:
        verbose_name = "Configuração Geral"
        verbose_name_plural = "Configurações Gerais"



class ConfiguracaoEmail(models.Model):
    """
    Modelo Singleton para armazenar as credenciais do servidor SMTP.
    """
    servidor_smtp = models.CharField("Servidor SMTP (Host)", max_length=255, default="smtp.gmail.com")
    porta = models.IntegerField("Porta", default=587)
    usuario = models.CharField("Usuário (E-mail)", max_length=255, blank=True, null=True, help_text="Ex: seu-email@gmail.com")
    senha = models.CharField("Senha / App Password", max_length=255, blank=True, null=True, help_text="Senha do e-mail ou senha de aplicativo (App Password)")
    usar_tls = models.BooleanField("Usar TLS", default=True)
    usar_ssl = models.BooleanField("Usar SSL", default=False)
    email_remetente = models.EmailField("E-mail do Remetente (De)", default="nao-responda@meusistema.com", help_text="O e-mail que aparecerá como remetente para os utilizadores.")

    def save(self, *args, **kwargs):
        self.pk = 1
        super(ConfiguracaoEmail, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

    class Meta:
        verbose_name = "Servidor de E-mail"
        verbose_name_plural = "Servidor de E-mail"

    def __str__(self):
        return f"SMTP: {self.servidor_smtp}:{self.porta}"

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

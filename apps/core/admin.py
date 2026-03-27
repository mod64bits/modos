from django.contrib import admin
from django import forms
from .models import ConfiguracaoGeral, ConfiguracaoEmail

@admin.register(ConfiguracaoGeral)
class ConfiguracaoGeralAdmin(admin.ModelAdmin):
    # Remove o botão de adicionar se já existir um registro
    def has_add_permission(self, request):
        return not ConfiguracaoGeral.objects.exists()

    # Remove o botão de deletar (ninguém deve apagar a config principal)
    def has_delete_permission(self, request, obj=None):
        return False

    fieldsets = (
        ('Identidade Visual e Links', {
            'fields': ('titulo_sistema', 'texto_rodape', 'site_url')
        }),
        ('Dados da Sua Empresa (Para Cabeçalhos de PDF)', {
            'fields': ('empresa_nome', 'empresa_cnpj', 'empresa_telefone', 'empresa_email', 'empresa_endereco')
        }),
    )
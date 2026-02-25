from django.contrib import admin

from django.contrib import admin
from .models import ConfiguracaoGeral

@admin.register(ConfiguracaoGeral)
class ConfiguracaoGeralAdmin(admin.ModelAdmin):
    # Remove o botão de adicionar se já existir um registro
    def has_add_permission(self, request):
        return not ConfiguracaoGeral.objects.exists()

    # Remove o botão de deletar (ninguém deve apagar a config principal)
    def has_delete_permission(self, request, obj=None):
        return False

    fieldsets = (
        ('Identidade Visual', {
            'fields': ('titulo_sistema', 'texto_rodape')
        }),
    )

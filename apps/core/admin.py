from django.contrib import admin
from django import forms
from django.contrib import admin
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
        ('Identidade Visual', {
            'fields': ('titulo_sistema', 'texto_rodape', 'site_url')
        }),
    )


class ConfiguracaoEmailForm(forms.ModelForm):
    class Meta:
        model = ConfiguracaoEmail
        fields = '__all__'
        widgets = {
            'senha': forms.PasswordInput(render_value=True),
        }

@admin.register(ConfiguracaoEmail)
class ConfiguracaoEmailAdmin(admin.ModelAdmin):
    form = ConfiguracaoEmailForm

    def has_add_permission(self, request):
        return not ConfiguracaoEmail.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    fieldsets = (
        ('Configurações do Servidor SMTP', {
            'fields': ('servidor_smtp', 'porta', 'usar_tls', 'usar_ssl')
        }),
        ('Autenticação', {
            'fields': ('usuario', 'senha')
        }),
        ('Remetente Padrão', {
            'fields': ('email_remetente',)
        }),
    )
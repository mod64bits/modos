from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario

@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    # Configuração para a tela de EDIÇÃO de usuário (já existente)
    fieldsets = UserAdmin.fieldsets + (
        ('Vínculo Corporativo', {
            'fields': ('empresa', 'setor', 'cargo'),
        }),
    )
    
    # Configuração para a tela de CRIAÇÃO de usuário (botão Adicionar)
    # Nota: O Django padrão primeiro pede usuário/senha e depois libera os outros campos na edição.
    # Mas deixamos configurado aqui caso use um form customizado no futuro.
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Vínculo Corporativo', {
            'fields': ('empresa', 'setor', 'cargo'),
        }),
    )

    # Colunas que aparecem na lista de todos os usuários
    list_display = ('username', 'email', 'first_name', 'empresa', 'setor', 'is_staff')
    
    # Filtros na barra lateral direita
    list_filter = ('empresa', 'setor', 'is_staff', 'is_active')
    
    # Campos que podem ser pesquisados
    search_fields = ('username', 'email', 'first_name', 'empresa__nome')

    # CORREÇÃO: Transforma o dropdown em campo de busca.
    # Se a lista não aparecia antes, agora você poderá pesquisar pelo nome da empresa.
    autocomplete_fields = ['empresa', 'setor']
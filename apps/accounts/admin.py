from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    # Configuração para a tela de EDIÇÃO de usuário
    fieldsets = UserAdmin.fieldsets + (
        ('Vínculo Corporativo', {
            'fields': ('empresa', 'setor', 'cargo'),
        }),
        ('Configurações de Atendimento (Técnico)', {
            'fields': ('is_tecnico', 'empresas_atendidas'),
        }),
    )

    # Configuração para a tela de CRIAÇÃO de usuário (botão Adicionar)
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Vínculo Corporativo', {
            'fields': ('empresa', 'setor', 'cargo'),
        }),
        ('Configurações de Atendimento (Técnico)', {
            'fields': ('is_tecnico', 'empresas_atendidas'),
        }),
    )

    # Colunas que aparecem na lista de todos os usuários
    list_display = ('username', 'email', 'first_name', 'empresa', 'setor', 'is_staff', 'is_tecnico')

    # Filtros na barra lateral direita
    list_filter = ('empresa', 'setor', 'is_staff', 'is_active', 'is_tecnico')

    # Campos que podem ser pesquisados
    search_fields = ('username', 'email', 'first_name', 'empresa__nome')

    # Autocompletar para otimizar o carregamento de muitas empresas/setores
    autocomplete_fields = ['empresa', 'setor']

    # ================================================================
    # AQUI ESTÁ A "MÁGICA" DA IMAGEM:
    # Transforma o campo "empresas_atendidas" num widget de duas colunas
    # ================================================================
    filter_horizontal = ('groups', 'user_permissions', 'empresas_atendidas')
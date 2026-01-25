from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario

@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    # Fieldsets define o layout do formulário de EDIÇÃO de usuário
    fieldsets = UserAdmin.fieldsets + (
        ('Vínculo Corporativo', {
            'fields': ('empresa', 'setor', 'cargo'),
        }),
    )
    
    # Add_fieldsets define o formulário de CRIAÇÃO de usuário
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Vínculo Corporativo', {
            'fields': ('empresa', 'setor', 'cargo'),
        }),
    )

    # Colunas na tabela de listagem de usuários
    list_display = ('username', 'email', 'get_full_name', 'empresa', 'setor', 'cargo', 'is_staff')
    
    # Filtros laterais
    list_filter = ('empresa', 'is_staff', 'is_active', 'groups')
    
    # Campos pesquisáveis
    search_fields = ('username', 'email', 'first_name', 'empresa__nome')
    
    # Ordenação padrão
    ordering = ('empresa', 'username')

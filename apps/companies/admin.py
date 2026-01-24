from django.contrib import admin
from .models import Empresa, Setor


class SetorInline(admin.TabularInline):
    model = Setor
    extra = 1 # Quantidade de linhas vazias extras para adicionar novos setores



@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    # Campos a serem exibidos na tabela de listagem
    list_display = ('nome', 'cnpj', 'email', 'telefone_responsavel', 'criado_em')
    
    # Habilita a edição destes campos diretamente na visualização de lista
    list_editable = ('email', 'telefone_responsavel')
    
    # Campos que podem ser pesquisados na barra de busca
    search_fields = ('nome', 'cnpj', 'email')
    
    # Filtros laterais para facilitar a navegação
    list_filter = ('criado_em', 'atualizado_em')
    
    # Define campos como somente leitura no formulário de detalhes
    readonly_fields = ('id', 'criado_em', 'atualizado_em')
    
    # Organização dos campos no formulário de edição (opcional, mas recomendado)
    fieldsets = (
        ('Dados Principais', {
            'fields': ('id', 'nome', 'cnpj')
        }),
        ('Contato', {
            'fields': ('email', 'telefone_responsavel')
        }),
        ('Metadados', {
            'fields': ('criado_em', 'atualizado_em'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Setor)
class SetorAdmin(admin.ModelAdmin):
    list_display = ('nome', 'empresa', 'descricao')
    list_filter = ('empresa',)
    search_fields = ('nome', 'empresa__nome')
    autocomplete_fields = ['empresa']  # Útil se houver muitas empresas



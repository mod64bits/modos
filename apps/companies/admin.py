from django.contrib import admin
from .models import Empresa, Setor

# Permite adicionar setores diretamente dentro da tela da Empresa
class SetorInline(admin.TabularInline):
    model = Setor
    extra = 1

@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cnpj', 'email', 'telefone_responsavel', 'criado_em')
    search_fields = ('nome', 'cnpj')
    inlines = [SetorInline]

@admin.register(Setor)
class SetorAdmin(admin.ModelAdmin):
    list_display = ('nome', 'empresa', 'descricao')
    list_filter = ('empresa',)
    search_fields = ('nome',) # Adicionado: Obrigatório para o autocomplete funcionar
    autocomplete_fields = ['empresa']  # Útil se houver muitas empresas



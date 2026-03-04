from django.contrib import admin
from .models import Chamado, CategoriaServico, LogEmail
from django.utils import timezone



@admin.register(CategoriaServico)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome',)

@admin.register(Chamado)
class ChamadoAdmin(admin.ModelAdmin):
    list_display = ('numero', 'titulo', 'solicitante', 'empresa', 'status', 'prioridade', 'tecnico_atribuido')
    list_filter = ('status', 'prioridade', 'tipo', 'empresa', 'categoria')
    search_fields = ('numero', 'titulo', 'descricao', 'solicitante__username', 'equipamento__serial')
    
    readonly_fields = ('numero', 'aberto_em', 'fechado_em')
    
    fieldsets = (
        ('Abertura', {
            'fields': ('numero', 'aberto_em', 'empresa', 'solicitante', 'setor')
        }),
        ('Classificação', {
            'fields': ('categoria', 'tipo', 'prioridade', 'status')
        }),
        ('Detalhes', {
            'fields': ('titulo', 'descricao', 'equipamento')
        }),
        ('Atendimento Técnico', {
            'fields': ('tecnico_atribuido', 'relatorio_tecnico', 'fechado_em')
        }),
    )

    # Ação rápida para fechar chamado
    actions = ['fechar_chamados']

    @admin.action(description='Fechar chamados selecionados')
    def fechar_chamados(self, request, queryset):
        queryset.update(status='RESOLVIDO', fechado_em=timezone.now())


@admin.register(LogEmail)
class LogEmailAdmin(admin.ModelAdmin):
    list_display = ('chamado', 'assunto', 'status', 'criado_em')
    list_filter = ('status', 'criado_em')
    search_fields = ('chamado__numero', 'assunto', 'destinatarios', 'erro_mensagem')
    
    # Impede a edição do log (Auditoria Pura)
    readonly_fields = ('chamado', 'assunto', 'destinatarios', 'status', 'erro_mensagem', 'criado_em', 'atualizado_em')

    # Remove a opção de adicionar manualmente, pois é o sistema que gera os logs
    def has_add_permission(self, request):
        return False
from django.contrib import admin
from .models import Equipamento, Computador, Disco, Periferico

# Permite adicionar discos direto na tela do Computador
class DiscoInline(admin.TabularInline):
    model = Disco
    extra = 1

# Permite ver quais periféricos estão ligados a este PC (somente leitura ou edição básica)
class PerifericoInline(admin.TabularInline):
    model = Periferico
    fk_name = 'conectado_a'
    extra = 0
    fields = ('tipo', 'marca', 'modelo', 'serial')
    readonly_fields = ('tipo', 'marca', 'modelo', 'serial') # Geralmente editamos o periférico na tela dele
    can_delete = False
    show_change_link = True # Botão para ir editar o periférico completo

@admin.register(Computador)
class ComputadorAdmin(admin.ModelAdmin):
    list_display = ('nome', 'empresa', 'responsavel', 'processador', 'resumo_discos')
    list_filter = ('empresa', 'setor')
    search_fields = ('nome', 'serial', 'responsavel__username', 'empresa__nome')
    
    # Adicionamos os inlines para gestão centralizada
    inlines = [DiscoInline, PerifericoInline]

    fieldsets = (
        ('Identificação', {
            'fields': ('empresa', 'setor', 'responsavel', 'nome')
        }),
        ('Detalhes Técnicos', {
            'fields': ('marca', 'modelo', 'serial', 'data_aquisicao')
        }),
        ('Hardware', {
            'fields': ('processador', 'memoria_ram')
        }),
    )

    # Método auxiliar para mostrar discos na lista
    def resumo_discos(self, obj):
        discos = obj.discos.all()
        return ", ".join([str(d) for d in discos])
    resumo_discos.short_description = "Armazenamento"

@admin.register(Periferico)
class PerifericoAdmin(admin.ModelAdmin):
    list_display = ('tipo', 'marca', 'modelo', 'conectado_a', 'empresa')
    list_filter = ('tipo', 'empresa', 'conectado_a')
    search_fields = ('marca', 'modelo', 'serial')
    
    # Se o periférico estiver conectado, mostramos onde.
    # Se não, ele está livre/estoque.

# Opcional: Registrar Equipamento base se quiser uma visão geral de TUDO
@admin.register(Equipamento)
class EquipamentoGeralAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tipo_real', 'empresa', 'serial')
    list_filter = ('empresa',)
    
    def tipo_real(self, obj):
        # Tenta descobrir se é computador ou periférico
        if hasattr(obj, 'computador'):
            return "Computador"
        if hasattr(obj, 'periferico'):
            return f"Periférico ({obj.periferico.tipo})"
        return "Equipamento Genérico"
    tipo_real.short_description = "Tipo"
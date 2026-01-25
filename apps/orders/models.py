import uuid
from django.db import models
from django.utils import timezone

from apps.accounts.models import Usuario
from apps.equipment.models import Equipamento
from apps.companies.models import Empresa, Setor

class CategoriaServico(models.Model):
    """
    Categorias para organizar os chamados.
    Ex: Hardware, Software, Rede, Impressoras, Acesso/VPN.
    """
    nome = models.CharField(max_length=50)
    descricao = models.TextField(blank=True)

    
    def __str__(self):
        return self.nome


class Chamado(models.Model):
    TIPO_CHOICES = [
        ('CORRETIVA', 'Manutenção Corretiva (Quebra/Erro)'),
        ('PREVENTIVA', 'Manutenção Preventiva'),
        ('REQUISICAO', 'Requisição de Serviço (Config/Instalação)'),
        ('DUVIDA', 'Dúvida / Suporte'),
    ]

    PRIORIDADE_CHOICES = [
        ('BAIXA', 'Baixa'),
        ('MEDIA', 'Média'),
        ('ALTA', 'Alta'),
        ('CRITICA', 'Crítica - Parada de Produção'),
    ]

    STATUS_CHOICES = [
        ('ABERTO', 'Aberto'),
        ('EM_ATENDIMENTO', 'Em Atendimento'),
        ('AGUARDANDO_PECA', 'Aguardando Peças/Terceiros'),
        ('RESOLVIDO', 'Resolvido'),
        ('CANCELADO', 'Cancelado'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    numero = models.PositiveIntegerField("Nº Protocolo", unique=True, editable=False)
    
    # Quem solicitou
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    solicitante = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='chamados_abertos')
    setor = models.ForeignKey(Setor, on_delete=models.SET_NULL, null=True, blank=True)
    
    # O que é
    categoria = models.ForeignKey(CategoriaServico, on_delete=models.SET_NULL, null=True)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='REQUISICAO')
    titulo = models.CharField("Assunto", max_length=100)
    descricao = models.TextField("Descrição do Problema/Solicitação")
    
    # Vínculo com Equipamento (Opcional - só preenche se for manutenção física)
    equipamento = models.ForeignKey(
        Equipamento, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='historico_chamados',
        help_text="Selecione se o chamado for referente a um equipamento específico."
    )

    # Quem resolve
    tecnico_atribuido = models.ForeignKey(
        Usuario, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='chamados_tecnicos',
        verbose_name="Técnico Responsável",
        limit_choices_to={'is_staff': True} # Garante que só usuários 'Staff' apareçam aqui
    )
    
    prioridade = models.CharField(max_length=10, choices=PRIORIDADE_CHOICES, default='MEDIA')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ABERTO')
    
    # Datas
    aberto_em = models.DateTimeField(auto_now_add=True)
    fechado_em = models.DateTimeField(null=True, blank=True)
    
    # Solução
    relatorio_tecnico = models.TextField("Laudo/Solução", blank=True, help_text="Descreva o que foi feito.")

    # Campo novo para auditoria de trocas
    historico_transferencias = models.TextField(
        "Log de Transferências", 
        blank=True, 
        default="", 
        editable=False, 
        help_text="Registro automático de trocas de técnicos."
    )

    class Meta:
        ordering = ['-aberto_em']
        verbose_name = "Chamado / O.S."
        verbose_name_plural = "Chamados e O.S."

    def save(self, *args, **kwargs):
        # 1. Geração Automática de Número de Protocolo
        if not self.numero:
            last = Chamado.objects.all().order_by('numero').last()
            self.numero = (last.numero + 1) if last else 1000
            
        # 2. Lógica de Transferência de Técnico
        if self.pk: # Se o chamado já existe (é uma edição)
            try:
                old_instance = Chamado.objects.get(pk=self.pk)
                # Verifica se o técnico mudou
                if old_instance.tecnico_atribuido != self.tecnico_atribuido:
                    old_name = old_instance.tecnico_atribuido.username if old_instance.tecnico_atribuido else "Ninguém"
                    new_name = self.tecnico_atribuido.username if self.tecnico_atribuido else "Ninguém"
                    
                    # Adiciona linha no log
                    log_entry = f"[{timezone.now().strftime('%d/%m/%Y %H:%M')}] Transferido de {old_name} para {new_name}\n"
                    self.historico_transferencias += log_entry
                    
                    # Se atribuiu alguém e estava 'ABERTO', muda para 'EM_ATENDIMENTO'
                    if self.tecnico_atribuido and self.status == 'ABERTO':
                        self.status = 'EM_ATENDIMENTO'
            except Chamado.DoesNotExist:
                pass # Caso raro de race condition, ignora

        super().save(*args, **kwargs)

    def __str__(self):
        return f"#{self.numero} - {self.titulo}"
import uuid
from decimal import Decimal
from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from apps.companies.models import Empresa


class Produto(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nome = models.CharField("Nome do Produto", max_length=200)
    fabricante = models.CharField("Fabricante", max_length=100)
    modelo = models.CharField("Modelo", max_length=100)
    descricao = models.TextField("Descrição", blank=True)
    valor_compra = models.DecimalField("Valor de Compra (R$)", max_digits=10, decimal_places=2)
    link_produto = models.URLField("Link do Produto", blank=True, help_text="Link do fornecedor (Opcional)")

    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Produto"
        verbose_name_plural = "Produtos"

    def __str__(self):
        return f"{self.nome} - {self.fabricante} {self.modelo}"


class Orcamento(models.Model):
    STATUS_CHOICES = [
        ('NAO_ENVIADO', 'Não Enviado'),
        ('EM_ANALISE', 'Em Análise (Enviado)'),
        ('APROVADO', 'Aprovado'),
        ('REPROVADO', 'Reprovado'),
        ('CONCLUIDO', 'Concluído'),
        ('CANCELADO', 'Cancelado'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    numero = models.PositiveIntegerField("Nº Orçamento", unique=True, editable=False)

    # Suporte a Clientes Cadastrados ou Avulsos
    empresa = models.ForeignKey(Empresa, on_delete=models.SET_NULL, null=True, blank=True, related_name='orcamentos',
                                help_text="Selecione caso seja um cliente cadastrado.")
    cliente_avulso_nome = models.CharField("Nome do Cliente (Avulso)", max_length=200, blank=True)
    cliente_avulso_contato = models.CharField("Contato (E-mail/Telefone)", max_length=200, blank=True)

    validade = models.DateField("Validade do Orçamento")
    status = models.CharField("Status", max_length=20, choices=STATUS_CHOICES, default='NAO_ENVIADO')
    descricao_geral = models.TextField("Descrição Geral do Serviço",
                                       help_text="Explique o escopo do projeto ou manutenção.")

    # Código único de acesso para o cliente
    hash_acesso = models.CharField("Código de Acesso", max_length=6, unique=True, blank=True, editable=False)
    total_mao_de_obra = models.DecimalField("Total Mão de Obra (R$)", max_digits=10, decimal_places=2,
                                            default=Decimal('0.00'))
    total_insumos = models.DecimalField("Total Insumos/Gastos (R$)", max_digits=10, decimal_places=2,
                                        default=Decimal('0.00'),
                                        help_text="Gastos com deslocamento, pedágio, alimentação, etc.")

    # Campos Calculados Automaticamente (ReadOnly)
    total_produtos_compra = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'),
                                                editable=False)
    total_produtos_venda = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), editable=False)
    valor_total_orcamento = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'),
                                                editable=False)
    lucro_equipamentos = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), editable=False)
    lucro_total_bruto = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), editable=False)
    lucro_total_liquido = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), editable=False)

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-numero']
        verbose_name = "Orçamento"
        verbose_name_plural = "Orçamentos"

    @property
    def nome_cliente(self):
        if self.empresa:
            return self.empresa.nome
        return f"{self.cliente_avulso_nome} (Avulso)"

    def save(self, *args, **kwargs):
        if not self.numero:
            last = Orcamento.objects.all().order_by('numero').last()
            self.numero = (last.numero + 1) if last else 5000

        # Converte tudo explicitamente para Decimal para evitar o erro TypeError (Float + Decimal)
        venda = Decimal(str(self.total_produtos_venda or '0.00'))
        compra = Decimal(str(self.total_produtos_compra or '0.00'))
        mao_de_obra = Decimal(str(self.total_mao_de_obra or '0.00'))
        insumos = Decimal(str(self.total_insumos or '0.00'))

        # Cálculos Financeiros Base
        self.valor_total_orcamento = venda + mao_de_obra
        self.lucro_equipamentos = venda - compra
        self.lucro_total_bruto = self.lucro_equipamentos + mao_de_obra
        self.lucro_total_liquido = self.lucro_total_bruto - insumos

        super().save(*args, **kwargs)

    def atualizar_totais(self):
        """ Recalcula a soma dos itens e salva o orçamento """
        itens = self.itens.all()
        self.total_produtos_compra = sum((item.valor_unitario_compra_registrado * item.quantidade) for item in itens)
        self.total_produtos_venda = sum((item.valor_unitario_venda * item.quantidade) for item in itens)
        self.save()

    def __str__(self):
        return f"Orçamento #{self.numero} - {self.nome_cliente}"


class ItemProdutoOrcamento(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    orcamento = models.ForeignKey(Orcamento, on_delete=models.CASCADE, related_name='itens')
    produto = models.ForeignKey(Produto, on_delete=models.PROTECT)
    quantidade = models.PositiveIntegerField(default=1)

    porcentagem_markup = models.DecimalField("Markup (%)", max_digits=5, decimal_places=2, default=0.00,
                                             help_text="Porcentagem de lucro sobre o valor de compra.")

    # Snapshot: Guarda o valor no momento da adição, caso o valor base mude no futuro
    valor_unitario_compra_registrado = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    valor_unitario_venda = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    valor_total_venda = models.DecimalField(max_digits=10, decimal_places=2, editable=False)

    def save(self, *args, **kwargs):
        # Regista o valor de compra atual
        self.valor_unitario_compra_registrado = self.produto.valor_compra

        # Calcula o valor de venda com base no Markup: Venda = Compra * (1 + (Markup / 100))
        markup_multiplier = Decimal('1') + (self.porcentagem_markup / Decimal('100'))
        self.valor_unitario_venda = self.valor_unitario_compra_registrado * markup_multiplier
        self.valor_total_venda = self.valor_unitario_venda * Decimal(str(self.quantidade))

        super().save(*args, **kwargs)


# === GATILHOS (SIGNALS) PARA RECALCULAR TOTAIS AUTOMATICAMENTE ===
@receiver(post_save, sender=ItemProdutoOrcamento)
@receiver(post_delete, sender=ItemProdutoOrcamento)
def atualizar_orcamento_ao_alterar_item(sender, instance, **kwargs):
    instance.orcamento.atualizar_totais()
import uuid
from django.db import models

class Empresa(models.Model):
    # ID utilizando UUID como chave primária
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    nome = models.CharField(
        max_length=255,
        verbose_name="Nome da Empresa"
    )
    
    # CNPJ geralmente tem 14 números ou 18 caracteres com pontuação
    # unique=True garante que não existam dois cadastros com o mesmo CNPJ
    cnpj = models.CharField(
        max_length=18,
        unique=True,
        verbose_name="CNPJ"
    )
    
    email = models.EmailField(
        verbose_name="E-mail de Contato"
    )
    
    telefone_responsavel = models.CharField(
        max_length=20,
        verbose_name="Telefone do Responsável",
        help_text="Formato: (XX) XXXXX-XXXX"
    )
    
    # É boa prática registrar quando o cadastro foi criado
    criado_em = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data de Cadastro"
    )

    # Atualizado automaticamente sempre que salvar
    atualizado_em = models.DateTimeField(
        auto_now=True,
        verbose_name="Última Atualização"
    )

    class Meta:
        verbose_name = "Empresa"
        verbose_name_plural = "Empresas"
        ordering = ['nome']

    def __str__(self):
        return f"{self.nome} ({self.cnpj})"
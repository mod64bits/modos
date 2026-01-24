import uuid
from django.db import models
from apps.accounts.models import Usuario
from apps.companies.models import Empresa, Setor



class Equipamento(models.Model):
    """
    Modelo base que contém as informações comuns a todos equipamento
    (seja ele um PC, um monitor, uma impressora, etc).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Vínculos organizacionais
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='equipamentos')
    setor = models.ForeignKey(Setor, on_delete=models.SET_NULL, null=True, blank=True)
    responsavel = models.ForeignKey(
        Usuario, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name="Usuário Responsável",
        help_text="Quem está utilizando o equipamento atualmente."
    )
    
    # Dados do Ativo
    nome = models.CharField("Nome/Identificação", max_length=100, help_text="Ex: Notebook do João")
    marca = models.CharField(max_length=50)
    modelo = models.CharField(max_length=50)
    serial = models.CharField("Número de Série", max_length=100, blank=True, null=True, unique=True)
    data_aquisicao = models.DateField("Data de Aquisição", blank=True, null=True)
    
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Equipamento"
        verbose_name_plural = "Equipamentos (Geral)"

    def __str__(self):
        return f"{self.nome} - {self.modelo} ({self.serial or 'S/N'})"


class Computador(Equipamento):
    """
    Herda tudo de Equipamento e adiciona especificidades de hardware.
    """
    processador = models.CharField(max_length=100, help_text="Ex: Intel Core i7 12ª Ger")
    memoria_ram = models.CharField("Memória RAM", max_length=50, help_text="Ex: 16GB DDR4")
    
    # O armazenamento é feito via modelo separado (Disco) para suportar múltiplos discos (SSD + HD)

    class Meta:
        verbose_name = "Computador"
        verbose_name_plural = "Computadores"


class Disco(models.Model):
    """
    Representa um dispositivo de armazenamento dentro de um computador.
    Permite que um PC tenha múltiplos discos (Ex: 1 SSD de Sistema + 1 HD de Arquivos).
    """
    TIPO_CHOICES = [
        ('HDD', 'Disco Rígido (HDD)'),
        ('SSD', 'SSD SATA'),
        ('NVME', 'SSD NVMe/M.2'),
    ]

    computador = models.ForeignKey(Computador, on_delete=models.CASCADE, related_name='discos')
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, default='SSD')
    tamanho = models.CharField(max_length=50, help_text="Ex: 512GB, 1TB")
    
    def __str__(self):
        return f"{self.tamanho} {self.tipo}"


class Periferico(Equipamento):
    """
    Periféricos também são equipamentos (têm marca/modelo/serial), 
    mas podem estar conectados a um computador pai.
    """
    TIPO_CHOICES = [
        ('MONITOR', 'Monitor'),
        ('TECLADO', 'Teclado'),
        ('MOUSE', 'Mouse'),
        ('HEADSET', 'Headset'),
        ('IMPRESSORA', 'Impressora'),
        ('OUTRO', 'Outro'),
    ]

    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    
    # Estratégia de Controle: FOREIGN KEY para o Computador.
    # Se estiver NULL, o periférico está no estoque ou avulso.
    # Se preenchido, sabemos exatamente em qual máquina ele está plugado.
    conectado_a = models.ForeignKey(
        Computador, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='perifericos_conectados',
        verbose_name="Conectado ao Computador"
    )

    class Meta:
        verbose_name = "Periférico"
        verbose_name_plural = "Periféricos"


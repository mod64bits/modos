import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from apps.companies.models import Empresa, Setor 



class Usuario(AbstractUser):
    # Removemos o username se quiser usar email como login (opcional)
    # Aqui mantemos o padrão, mas adicionamos os vínculos:
    empresa = models.ForeignKey(
        Empresa, 
        on_delete=models.CASCADE, 
        related_name='usuarios',
        null=True, 
        blank=True,
        help_text="Empresa à qual este usuário pertence."
    )
    setor = models.ForeignKey(
        Setor,
        on_delete=models.SET_NULL,
        related_name='usuarios',
        null=True,
        blank=True,
        help_text="Setor de atuação do usuário."
    )
    cargo = models.CharField("Cargo", max_length=100, blank=True)


    def __str__(self):
        if self.empresa:
            return f"{self.username} | {self.empresa.nome}"
        return self.username

    class Meta:
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"
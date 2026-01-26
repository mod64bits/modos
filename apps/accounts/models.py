import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser



class Usuario(AbstractUser):
    # Removemos o username se quiser usar email como login (opcional)
    # Aqui mantemos o padrão, mas adicionamos os vínculos:
    
    empresa = models.ForeignKey(
        "companies.empresa", 
        on_delete=models.CASCADE, 
        related_name='usuarios',
        null=True, 
        blank=True,
        help_text="Empresa à qual este usuário pertence."
    )
    
    setor = models.ForeignKey(
        "companies.setor",
        on_delete=models.SET_NULL,
        related_name='usuarios',
        null=True,
        blank=True,
        help_text="Setor de atuação do usuário."
    )

    cargo = models.CharField("Cargo", max_length=100, blank=True)

    # CORREÇÃO DOS ERROS DE CLASH (Conflito)
    # Redefinimos os campos com related_name personalizados para evitar conflito com auth.User
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_name="usuario_set",
        related_query_name="usuario",
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="usuario_set",
        related_query_name="usuario",
    )

    class Meta:
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"

    def __str__(self):
        if self.empresa:
            return f"{self.username} | {self.empresa.nome}"
        return self.username
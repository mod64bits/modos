from django.core.exceptions import PermissionDenied

class EmpresaFilterMixin:
    """
    Mixin para Views baseadas em classe (CBV).
    Sobrescreve o get_queryset para filtrar apenas dados da empresa do utilizador logado.
    """
    def get_queryset(self):
        # Pega a query original definida na View
        queryset = super().get_queryset()
        
        # Se for superutilizador, vê tudo (opcional, bom para debug)
        if self.request.user.is_superuser:
            return queryset
            
        # Verifica se o utilizador tem empresa vinculada
        if not getattr(self.request.user, 'empresa', None):
            # Retorna lista vazia se utilizador não tiver empresa (segurança)
            return queryset.none()

        # Filtra os dados onde o campo 'empresa' é igual à empresa do utilizador
        # IMPORTANTE: Os seus outros models devem ter um campo 'empresa'
        return queryset.filter(empresa=self.request.user.empresa)
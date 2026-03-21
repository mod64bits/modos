from django.urls import path
from .views import DashboardUserView, DashboardAdminView, AssignTicketView

from .views_cadastros import (
    EmpresaListView, EmpresaCreateView,
    EquipamentoListView, EquipamentoCreateView,
    CategoriaListView, CategoriaCreateView
)


app_name = "dashboard"

urlpatterns = [
    path("", DashboardUserView.as_view(), name="dashboard_user"),
    path("dashboard/admin/", DashboardAdminView.as_view(), name="dashboard_admin"),
    # Ação de puxar a O.S. para o técnico logado
    path("admin/atribuir/<uuid:pk>/", AssignTicketView.as_view(), name="assign_ticket"),
    path('cadastros/empresas/', EmpresaListView.as_view(), name='empresa_list'),
    path('cadastros/empresas/nova/', EmpresaCreateView.as_view(), name='empresa_create'),

    path('cadastros/equipamentos/', EquipamentoListView.as_view(), name='equipamento_list'),
    path('cadastros/equipamentos/novo/', EquipamentoCreateView.as_view(), name='equipamento_create'),

    path('cadastros/categorias/', CategoriaListView.as_view(), name='categoria_list'),
    path('cadastros/categorias/nova/', CategoriaCreateView.as_view(), name='categoria_create'),
]

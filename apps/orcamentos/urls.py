from django.urls import path
from .views import (
    OrcamentoListView,
    OrcamentoCreateView,
    OrcamentoDetailView,
    deletar_item_orcamento,
    api_detalhes_produto
)

app_name = "orcamentos"

urlpatterns = [
    path('', OrcamentoListView.as_view(), name='orcamento_list'),
    path('novo/', OrcamentoCreateView.as_view(), name='orcamento_create'),
    path('<uuid:pk>/', OrcamentoDetailView.as_view(), name='orcamento_detail'),

    # Ações Extras
    path('item/<uuid:pk>/deletar/', deletar_item_orcamento, name='deletar_item_orcamento'),
    path('api/produto/<uuid:pk>/', api_detalhes_produto, name='api_detalhes_produto'),
]
from django.urls import path
from .views import (
    OrcamentoListView,
    OrcamentoCreateView,
    OrcamentoUpdateView,
    OrcamentoDetailView,
    deletar_item_orcamento,
    editar_item_orcamento,
    atualizar_status_orcamento,
    api_detalhes_produto,
    ProdutoListView,
    ProdutoCreateView
)

# Namespace para organizar as rotas deste app
app_name = 'orcamentos'

urlpatterns = [
    # Rotas principais de Orçamentos
    path('', OrcamentoListView.as_view(), name='orcamento_list'),
    path('novo/', OrcamentoCreateView.as_view(), name='orcamento_create'),
    path('<uuid:pk>/', OrcamentoDetailView.as_view(), name='orcamento_detail'),
    path('<uuid:pk>/editar/', OrcamentoUpdateView.as_view(), name='orcamento_update'),
    path('<uuid:pk>/status/', atualizar_status_orcamento, name='atualizar_status_orcamento'),

    # Ações Extras (API, Edição e Exclusão)
    path('item/<uuid:pk>/editar/', editar_item_orcamento, name='editar_item_orcamento'),
    path('item/<uuid:pk>/deletar/', deletar_item_orcamento, name='deletar_item_orcamento'),
    path('api/produto/<uuid:pk>/', api_detalhes_produto, name='api_detalhes_produto'),

    # Rotas do Catálogo de Produtos (Apenas Admin)
    path('produtos/', ProdutoListView.as_view(), name='produto_list'),
    path('produtos/novo/', ProdutoCreateView.as_view(), name='produto_create'),
]
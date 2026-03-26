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
    editar_produto_catalogo,
    deletar_produto_catalogo,
    ProdutoListView,
    ProdutoCreateView,
    OrcamentoPDFClienteView, # Nova View de PDF (Cliente)
    OrcamentoPDFInternoView  # Nova View de PDF (Gerencial/Técnico)
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

    # ROTAS DE PDF (Abrem numa nova aba do navegador)
    path('<uuid:pk>/pdf/cliente/', OrcamentoPDFClienteView.as_view(), name='orcamento_pdf_cliente'),
    path('<uuid:pk>/pdf/interno/', OrcamentoPDFInternoView.as_view(), name='orcamento_pdf_interno'),

    # Ações Extras de Itens (Edição e Exclusão no Orçamento)
    path('item/<uuid:pk>/editar/', editar_item_orcamento, name='editar_item_orcamento'),
    path('item/<uuid:pk>/deletar/', deletar_item_orcamento, name='deletar_item_orcamento'),

    # API de Preços
    path('api/produto/<uuid:pk>/', api_detalhes_produto, name='api_detalhes_produto'),

    # Rotas do Catálogo de Produtos (Apenas Admin)
    path('produtos/', ProdutoListView.as_view(), name='produto_list'),
    path('produtos/novo/', ProdutoCreateView.as_view(), name='produto_create'),
    path('produtos/<uuid:pk>/editar/', editar_produto_catalogo, name='produto_update'),
    path('produtos/<uuid:pk>/deletar/', deletar_produto_catalogo, name='produto_delete'),
]
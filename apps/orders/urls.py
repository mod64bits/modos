from django.urls import path
from .views import (
    ChamadoCreateView,
    ChamadoDetailView,
    ChamadoCancelView,
    AdicionarComentarioView,
    ChamadoPDFView,
    EnviarPDFEmailView,
    RelatorioFiltroView,
)

app_name = "orders"

urlpatterns = [
    path("novo/", ChamadoCreateView.as_view(), name="chamado_create"),
    path("detalhe/<uuid:pk>/", ChamadoDetailView.as_view(), name="chamado_detalhe"),
    path("<uuid:pk>/cancelar/", ChamadoCancelView.as_view(), name="chamado_cancel"),
    path(
        "<uuid:pk>/comentar/",
        AdicionarComentarioView.as_view(),
        name="chamado_comentar",
    ),
    # rotas do pdf
    path("<uuid:pk>/pdf/", ChamadoPDFView.as_view(), name="chamado_pdf"),
    path(
        "<uuid:pk>/enviar-pdf/", EnviarPDFEmailView.as_view(), name="enviar_pdf_email"
    ),
    path("relatorios/", RelatorioFiltroView.as_view(), name="relatorio_chamados"),
]

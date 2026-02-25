from django.urls import path
from .views import ChamadoCreateView, ChamadoDetailView, ChamadoCancelView, AdicionarComentarioView

app_name = 'orders'

urlpatterns = [
   
    path('novo/', ChamadoCreateView.as_view(), name='chamado_create'),
    path('detalhe/<uuid:pk>/', ChamadoDetailView.as_view(), name='chamado_detalhe'),
    path('<uuid:pk>/cancelar/', ChamadoCancelView.as_view(), name='chamado_cancel'),
    path('<uuid:pk>/comentar/', AdicionarComentarioView.as_view(), name='chamado_comentar'),
]
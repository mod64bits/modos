from django.urls import path
from .views import ChamadoCreateView, ChamadoDetailView, ChamadoCancelView

app_name = 'orders'

urlpatterns = [
   
    path('novo/', ChamadoCreateView.as_view(), name='chamado_create'),
    path('detalhe/<uuid:pk>/', ChamadoDetailView.as_view(), name='chamado_detalhe'),
    path('<uuid:pk>/cancelar/', ChamadoCancelView.as_view(), name='chamado_cancel'),
]
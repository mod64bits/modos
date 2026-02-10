from django.urls import path
from .views import ChamadoCreateView

app_name = 'orders'

urlpatterns = [
   
    path('novo/', ChamadoCreateView.as_view(), name='chamado_create'),
]
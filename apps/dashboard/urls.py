from django.urls import path
from .views import DashboardUserView


app_name = 'dashboard'

urlpatterns = [
    path('user/', DashboardUserView.as_view(), name='dashbord_user'),
]
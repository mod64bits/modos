from django.urls import path
from .views import DashboardUserView, DashboardAdminView, AssignTicketView


app_name = "dashboard"

urlpatterns = [
    path("", DashboardUserView.as_view(), name="dashbord_user"),
    path("dashboard/admin/", DashboardAdminView.as_view(), name="dashboard_admin"),
    # Ação de puxar a O.S. para o técnico logado
    path("admin/atribuir/<uuid:pk>/", AssignTicketView.as_view(), name="assign_ticket"),
]

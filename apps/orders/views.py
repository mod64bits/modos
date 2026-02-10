from django.views.generic import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Chamado
from .forms import ChamadoForm

class ChamadoCreateView(LoginRequiredMixin, CreateView):
    model = Chamado
    form_class = ChamadoForm
    template_name = 'orders/chamado_form.html'
    # Ajuste 'dashboard' para o nome da rota da sua DashboardUserView no urls.py
    success_url = reverse_lazy('dashboard:dashbord_user') 

    def get_form_kwargs(self):
        """Passa o usuário logado para o formulário (para filtrar equipamentos)"""
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        """Preenche campos automáticos antes de salvar"""
        chamado = form.save(commit=False)
        
        # Define quem abriu o chamado
        chamado.solicitante = self.request.user
        
        # Define a empresa do chamado (baseada no usuário)
        if self.request.user.empresa:
            chamado.empresa = self.request.user.empresa
            
        chamado.save()
        messages.success(self.request, f"Chamado #{chamado.numero} aberto com sucesso!")
        return super().form_valid(form)
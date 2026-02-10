from django.views.generic import CreateView, DetailView
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



class ChamadoDetailView(LoginRequiredMixin, DetailView):
    model = Chamado
    template_name = 'orders/chamado_detail.html'
    context_object_name = 'chamado'

    def get_queryset(self):
        """
        Segurança: Garante que o usuário só consiga ver detalhes
        dos chamados que ELE MESMO abriu.
        """
        qs = super().get_queryset()
        # Se for Staff (Técnico), pode ver tudo. Se for usuário comum, só os dele.
        if self.request.user.is_staff:
            return qs
        return qs.filter(solicitante=self.request.user)
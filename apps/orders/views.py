from django.views.generic import CreateView, DetailView
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
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


class ChamadoCancelView(LoginRequiredMixin, View):
    def post(self, request, pk):
        # Busca o chamado, garantindo que pertence ao usuário logado
        chamado = get_object_or_404(Chamado, pk=pk, solicitante=request.user)
        
        # Só permite cancelar se estiver Aberto
        if chamado.status == 'ABERTO':
            chamado.status = 'CANCELADO'
            chamado.save()
            messages.success(request, f"Chamado #{chamado.numero} cancelado com sucesso.")
        else:
            messages.error(request, f"Não é possível cancelar este chamado (Status atual: {chamado.get_status_display()}).")
        
        # Redireciona de volta para o Dashboard
        return redirect('dashboard:dashbord_user')
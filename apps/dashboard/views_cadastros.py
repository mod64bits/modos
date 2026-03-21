from django.views.generic import ListView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.contrib import messages

from apps.companies.models import Empresa
from apps.equipment.models import Equipamento
from apps.orders.models import CategoriaServico
from .forms_cadastros import EmpresaForm, EquipamentoForm, CategoriaForm

class BaseStaffView(LoginRequiredMixin, UserPassesTestMixin):
    """ Garante que apenas Técnicos e Admins acedam a estas telas """
    def test_func(self):
        return self.request.user.is_staff

# ================= EMPRESAS =================
class EmpresaListView(BaseStaffView, ListView):
    model = Empresa
    template_name = 'dashboard/cadastros/empresa_list.html'
    context_object_name = 'empresas'

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.is_superuser:
            return qs
        elif getattr(user, 'is_tecnico', False):
            empresas_ids = set()
            if user.empresa_id: empresas_ids.add(user.empresa_id)
            if hasattr(user, 'empresas_atendidas'):
                empresas_ids.update(user.empresas_atendidas.values_list('id', flat=True))
            return qs.filter(id__in=empresas_ids)
        return qs.none()

class EmpresaCreateView(BaseStaffView, CreateView):
    model = Empresa
    form_class = EmpresaForm
    template_name = 'dashboard/cadastros/generic_form.html'
    success_url = reverse_lazy('dashboard:empresa_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = 'Cadastrar Nova Empresa'
        return ctx

    def form_valid(self, form):
        response = super().form_valid(form)
        user = self.request.user
        # MÁGICA: Se for técnico, vincula automaticamente a empresa a ele
        if getattr(user, 'is_tecnico', False) and not user.is_superuser:
            user.empresas_atendidas.add(self.object)
        messages.success(self.request, "Empresa cadastrada com sucesso!")
        return response

# ================= EQUIPAMENTOS =================
class EquipamentoListView(BaseStaffView, ListView):
    model = Equipamento
    template_name = 'dashboard/cadastros/equipamento_list.html'
    context_object_name = 'equipamentos'

    def get_queryset(self):
        qs = super().get_queryset().select_related('empresa')
        user = self.request.user
        if user.is_superuser:
            return qs
        elif getattr(user, 'is_tecnico', False):
            empresas_ids = set()
            if user.empresa_id: empresas_ids.add(user.empresa_id)
            if hasattr(user, 'empresas_atendidas'):
                empresas_ids.update(user.empresas_atendidas.values_list('id', flat=True))
            return qs.filter(empresa_id__in=empresas_ids)
        return qs.none()

class EquipamentoCreateView(BaseStaffView, CreateView):
    model = Equipamento
    form_class = EquipamentoForm
    template_name = 'dashboard/cadastros/generic_form.html'
    success_url = reverse_lazy('dashboard:equipamento_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = 'Cadastrar Equipamento'
        return ctx

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, "Equipamento cadastrado com sucesso!")
        return super().form_valid(form)

# ================= CATEGORIAS (SERVIÇOS) =================
class CategoriaListView(BaseStaffView, ListView):
    model = CategoriaServico
    template_name = 'dashboard/cadastros/categoria_list.html'
    context_object_name = 'categorias'

class CategoriaCreateView(BaseStaffView, CreateView):
    model = CategoriaServico
    form_class = CategoriaForm
    template_name = 'dashboard/cadastros/generic_form.html'
    success_url = reverse_lazy('dashboard:categoria_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = 'Cadastrar Categoria de Serviço'
        return ctx

    def form_valid(self, form):
        messages.success(self.request, "Categoria cadastrada com sucesso!")
        return super().form_valid(form)
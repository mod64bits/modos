import json
from django.views.generic import TemplateView
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Count
from apps.orders.models import Chamado


class DashboardUserView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/dashboard-user-view.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_staff:
            return redirect('dashboard:dashboard_admin')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        user = self.request.user
        qs = Chamado.objects.filter(solicitante=user).select_related('categoria')

        status_open_list = ['ABERTO', 'EM_ATENDIMENTO', 'AGUARDANDO_PECA']
        status_close_list = ['RESOLVIDO', 'CANCELADO']

        context['order_open'] = qs.filter(status__in=status_open_list).order_by('-aberto_em')
        context['order_close'] = qs.filter(status__in=status_close_list).order_by('-fechado_em')
        context['count_open'] = qs.filter(status__in=status_open_list).count()
        context['count_close'] = qs.filter(status__in=status_close_list).count()

        return context


class DashboardAdminView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'dashboard/dashboard-admin-view.html'

    def test_func(self):
        return self.request.user.is_staff

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        qs = Chamado.objects.all().select_related('categoria', 'solicitante', 'equipamento')

        # ==============================================================
        # 1. ISOLAMENTO MULTI-TENANT (MÉTODO À PROVA DE BALA POR IDs)
        # ==============================================================
        if getattr(user, 'is_tecnico', False):
            # REGRA 1: Se for Técnico (mesmo sendo Admin), fica RESTRITO às empresas vinculadas.
            empresas_ids = set()

            # A) Adiciona a empresa principal do utilizador logado
            if user.empresa_id:
                empresas_ids.add(user.empresa_id)

            # B) Adiciona todas as empresas que ele está autorizado a atender
            ids_atendidas = user.empresas_atendidas.values_list('id', flat=True)
            empresas_ids.update(ids_atendidas)

            # C) Aplica o filtro estrito
            if empresas_ids:
                qs = qs.filter(empresa_id__in=empresas_ids)
            else:
                qs = qs.none()  # Sem empresas vinculadas = Vê nada

        elif user.is_superuser:
            # REGRA 2: Se NÃO for técnico, mas for Admin Geral (Superuser), vê TUDO.
            pass

        else:
            # REGRA 3: Staff normal, vê apenas a própria empresa
            if user.empresa_id:
                qs = qs.filter(empresa_id=user.empresa_id)
            else:
                qs = qs.none()
        # ==============================================================

        # 2. Capturar filtros da URL (GET)
        status_filter = self.request.GET.get('status')
        if status_filter:
            qs = qs.filter(status=status_filter)

        # 3. Listas para as tabelas
        context['fila_chamados'] = qs.filter(status='ABERTO', tecnico_atribuido__isnull=True).order_by('aberto_em')

        context['meus_chamados'] = qs.filter(
            tecnico_atribuido=user,
            status__in=['ABERTO', 'EM_ATENDIMENTO', 'AGUARDANDO_PECA']
        ).order_by('aberto_em')

        # 4. Dados para os Cards e Gráficos
        context['total_abertos'] = qs.filter(status='ABERTO').count()
        context['total_atendimento'] = qs.filter(status='EM_ATENDIMENTO').count()
        context['total_resolvidos'] = qs.filter(status='RESOLVIDO').count()

        status_counts = qs.values('status').annotate(total=Count('id'))

        labels = []
        data = []
        status_dict = dict(Chamado.STATUS_CHOICES)

        for item in status_counts:
            labels.append(status_dict.get(item['status'], item['status']))
            data.append(item['total'])

        context['chart_labels'] = json.dumps(labels)
        context['chart_data'] = json.dumps(data)
        context['current_status'] = status_filter

        return context


class AssignTicketView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_staff

    def post(self, request, pk):
        chamado = get_object_or_404(Chamado, pk=pk)
        user = request.user

        # Verifica segurança: Multi-tenant
        has_permission = False

        if getattr(user, 'is_tecnico', False):
            # Técnico só puxa da sua base de clientes autorizada
            if user.empresas_atendidas.filter(id=chamado.empresa_id).exists() or user.empresa_id == chamado.empresa_id:
                has_permission = True
        elif user.is_superuser:
            # Admin Geral pode assumir qualquer um
            has_permission = True
        else:
            # Staff comum
            if user.empresa_id == chamado.empresa_id:
                has_permission = True

        if not has_permission:
            messages.error(request, "Você não tem permissão para assumir este chamado (Empresa não autorizada).")
            return redirect('dashboard:dashboard_admin')

        if not chamado.tecnico_atribuido:
            chamado.tecnico_atribuido = request.user
            chamado.status = 'EM_ATENDIMENTO'
            chamado.save()
            messages.success(request, f"O chamado #{chamado.numero} foi atribuído a você e está Em Atendimento.")
        else:
            messages.warning(request, f"O chamado #{chamado.numero} já possui um técnico responsável.")

        return redirect('dashboard:dashboard_admin')
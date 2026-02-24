import json
from django.views.generic import TemplateView
from django.db.models import Count
from django.views import View
from django.contrib import messages
from apps.orders.models import Chamado
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from apps.orders.models import Chamado  # Certifique-se que o import está correto para o seu app



class DashboardUserView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/dashboarduserview.html'

    def dispatch(self, request, *args, **kwargs):
        # Redireciona usuários com perfil de Admin/Técnico (Staff) para o seu próprio painel
        if request.user.is_authenticated and request.user.is_staff:
            return redirect('dashboard:dashboard_admin')
        return super().dispatch(request, *args, **kwargs)
    

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        
        # Pega o usuário logado
        user = self.request.user
        
        # Busca todas as ordens deste usuário
        # Nota: O select_related('categoria') otimiza a consulta se você for mostrar a categoria no template
        qs = Chamado.objects.filter(solicitante=user).select_related('categoria')
        
        # Define quais status contam como "Abertos" e "Fechados"
        status_open_list = ['ABERTO', 'EM_ATENDIMENTO', 'AGUARDANDO_PECA']
        status_close_list = ['RESOLVIDO', 'CANCELADO']

        # Filtra os querysets
        # order_open: Lista dos objetos (para fazer um {% for order in order_open %} no template)
        context['order_open'] = qs.filter(status__in=status_open_list).order_by('-aberto_em')
        
        # order_close: Lista dos objetos fechados
        context['order_close'] = qs.filter(status__in=status_close_list).order_by('-fechado_em')
        
        # Opcional: Contadores para exibir em cards (ex: "Você tem 3 chamados abertos")
        context['count_open'] = qs.filter(status__in=status_open_list).count()
        context['count_close'] = qs.filter(status__in=status_close_list).count()
        
        return context




class DashboardAdminView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'dashboard/dashboard-admin-view.html'

    def test_func(self):
        # Apenas usuários marcados como "Staff" (Técnicos/Admins) podem acessar
        return self.request.user.is_staff

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # 1. Isolamento Multi-tenant: Staff vê apenas os chamados da sua empresa (exceto superusers)
        qs = Chamado.objects.all().select_related('categoria', 'solicitante', 'equipamento')
        if not user.is_superuser and user.empresa:
            qs = qs.filter(empresa=user.empresa)

        # 2. Capturar filtros da URL (GET)
        status_filter = self.request.GET.get('status')
        if status_filter:
            qs = qs.filter(status=status_filter)

        # 3. Listas para as tabelas
        # Fila Geral: Abertos e sem técnico
        context['fila_chamados'] = qs.filter(status='ABERTO', tecnico_atribuido__isnull=True).order_by('aberto_em')
        
        # Meus Chamados: Atribuídos a mim e não finalizados
        context['meus_chamados'] = qs.filter(
            tecnico_atribuido=user, 
            status__in=['ABERTO', 'EM_ATENDIMENTO', 'AGUARDANDO_PECA']
        ).order_by('aberto_em')

        # 4. Dados para os Cards e Gráficos
        context['total_abertos'] = qs.filter(status='ABERTO').count()
        context['total_atendimento'] = qs.filter(status='EM_ATENDIMENTO').count()
        context['total_resolvidos'] = qs.filter(status='RESOLVIDO').count()

        # Agrupamento para o Gráfico de Status
        status_counts = qs.values('status').annotate(total=Count('id'))
        
        # Preparar dados para o Chart.js
        labels = []
        data = []
        # Traduzir a sigla do banco para o label legível
        status_dict = dict(Chamado.STATUS_CHOICES)
        
        for item in status_counts:
            labels.append(status_dict.get(item['status'], item['status']))
            data.append(item['total'])

        context['chart_labels'] = json.dumps(labels)
        context['chart_data'] = json.dumps(data)
        context['current_status'] = status_filter

        return context


class AssignTicketView(LoginRequiredMixin, UserPassesTestMixin, View):
    """
    View acionada quando o técnico clica em "Puxar O.S."
    """
    def test_func(self):
        return self.request.user.is_staff

    def post(self, request, pk):
        chamado = get_object_or_404(Chamado, pk=pk)
        
        # Verifica segurança: se não é superuser, o chamado deve ser da mesma empresa
        if not request.user.is_superuser and chamado.empresa != request.user.empresa:
            messages.error(request, "Você não tem permissão para assumir este chamado.")
            return redirect('dashboard:dashboard_admin')

        if not chamado.tecnico_atribuido:
            chamado.tecnico_atribuido = request.user
            # Ao puxar para si, muda o status para Em Atendimento
            chamado.status = 'EM_ATENDIMENTO'
            chamado.save()
            messages.success(request, f"O chamado #{chamado.numero} foi atribuído a você e está Em Atendimento.")
        else:
            messages.warning(request, f"O chamado #{chamado.numero} já possui um técnico responsável.")
            
        return redirect('dashboard:dashboard_admin')
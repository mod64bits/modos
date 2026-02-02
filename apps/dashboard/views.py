from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.orders.models import Chamado  # Certifique-se que o import está correto para o seu app


class DashboardUserView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/dashboard-user-view.html'

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
from django.views.generic import CreateView, DetailView
from django.views import View
from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy, reverse, NoReverseMatch
from django.contrib import messages
from .models import Chamado
from apps.companies.models import Empresa, Setor
from .forms import ChamadoForm, ComentarioForm
from apps.core.gerador_pdf import render_to_pdf

try:
    from apps.companies.models import Empresa
except ImportError:
    from apps.accounts.models import Empresa


class ChamadoCreateView(LoginRequiredMixin, CreateView):
    model = Chamado
    form_class = ChamadoForm
    template_name = "orders/chamado_form.html"
    # Ajuste 'dashboard' para o nome da rota da sua DashboardUserView no urls.py
    success_url = reverse_lazy("dashboard:dashboard_user")

    def get_form_kwargs(self):
        """Passa o usuário logado para o formulário (para filtrar equipamentos)"""
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        chamado = form.save(commit=False)
        chamado.solicitante = self.request.user
        if self.request.user.empresa:
            chamado.empresa = self.request.user.empresa

        # Guardamos o chamado APENAS UMA VEZ (dispara o e-mail de "Novo Chamado")
        chamado.save()
        self.object = chamado

        messages.success(self.request, f"Chamado #{chamado.numero} aberto com sucesso!")

        # Retornamos o redirecionamento diretamente.
        # Se chamássemos super().form_valid(form), o Django faria um segundo .save() automaticamente,
        # gerando o e-mail duplicado de "Atualização".
        from django.http import HttpResponseRedirect

        return HttpResponseRedirect(self.get_success_url())


class ChamadoDetailView(LoginRequiredMixin, DetailView):
    model = Chamado
    template_name = "orders/chamado_detail.html"
    context_object_name = "chamado"

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 1. Traz todos os comentários vinculados a este chamado
        context["comentarios"] = self.object.comentarios.select_related("autor").all()
        # 2. O SEGREDO ESTÁ AQUI: Enviar o formulário vazio para o template!
        # Sem essa variável 'comentario_form', os campos de texto não aparecem na tela.
        if self.object.status not in ["RESOLVIDO", "CANCELADO"]:
            context["comentario_form"] = ComentarioForm()
        return context


class ChamadoCancelView(LoginRequiredMixin, View):
    def post(self, request, pk):
        # Busca o chamado, garantindo que pertence ao usuário logado
        chamado = get_object_or_404(Chamado, pk=pk, solicitante=request.user)

        # Só permite cancelar se estiver Aberto
        if chamado.status == "ABERTO":
            chamado.status = "CANCELADO"
            chamado.save()
            messages.success(
                request, f"Chamado #{chamado.numero} cancelado com sucesso."
            )
        else:
            messages.error(
                request,
                f"Não é possível cancelar este chamado (Status atual: {chamado.get_status_display()}).",
            )

        # Redireciona de volta para o Dashboard
        return redirect("dashboard:dashboard_user")


class AdicionarComentarioView(LoginRequiredMixin, View):
    def post(self, request, pk):
        chamado = get_object_or_404(Chamado, pk=pk)

        # Helper robusto para resolver a URL de redirecionamento
        # (retorna para a página de onde o usuário veio)
        referer = request.META.get("HTTP_REFERER")
        if referer:
            redirect_url = referer
        else:
            try:
                redirect_url = reverse("orders:chamado_detail", kwargs={"pk": pk})
            except NoReverseMatch:
                try:
                    redirect_url = reverse("orders:chamado_detail", kwargs={"pk": pk})
                except NoReverseMatch:
                    redirect_url = reverse("dashboard:dashboard_user")

        # Validação de Segurança
        if not request.user.is_staff and chamado.solicitante != request.user:
            messages.error(
                request, "Você não tem permissão para interagir com este chamado."
            )
            return redirect(redirect_url)

        # Bloqueio de inserção caso finalizado/cancelado
        if chamado.status in ["RESOLVIDO", "CANCELADO"]:
            messages.error(
                request,
                "Este chamado já está encerrado e não aceita novos comentários.",
            )
            return redirect(redirect_url)

        # Trata os dados e o arquivo em anexo
        form = ComentarioForm(request.POST, request.FILES)
        if form.is_valid():
            comentario = form.save(commit=False)
            comentario.chamado = chamado
            comentario.autor = request.user
            comentario.save()
            messages.success(request, "Comentário adicionado com sucesso.")
        else:
            messages.error(
                request,
                "Erro ao adicionar comentário. Verifique se o arquivo enviado é válido.",
            )

        return redirect(redirect_url)


# ==========================================
# VIEWS PARA PDF E RELATÓRIOS (Multi-tenant)
# ==========================================


class ChamadoPDFView(LoginRequiredMixin, View):
    """ View para gerar e descarregar o PDF de um Chamado Específico """

    def get(self, request, pk):
        chamado = get_object_or_404(Chamado, pk=pk)
        user = request.user

        is_owner = (chamado.solicitante == user)
        is_finished = chamado.status in ['RESOLVIDO', 'CANCELADO']

        # 1. TÉCNICO VÊ APENAS O QUE LHE PERTENCE (Mesmo que seja admin)
        if getattr(user, 'is_tecnico', False):
            empresas_ids = set()
            if user.empresa_id:
                empresas_ids.add(user.empresa_id)
            if hasattr(user, 'empresas_atendidas'):
                empresas_ids.update(user.empresas_atendidas.values_list('id', flat=True))

            if chamado.empresa_id not in empresas_ids:
                messages.error(request, "Você não tem permissão para visualizar laudos desta empresa.")
                return redirect('dashboard:dashboard_admin')

        # 2. ADMIN GERAL TEM ACESSO TOTAL
        elif user.is_superuser:
            pass

            # 3. CLIENTE COMUM OU STAFF NORMAL
        else:
            if not (is_owner and is_finished) and not user.is_staff:
                messages.error(request, "O PDF do laudo só fica disponível após o encerramento da O.S.")
                return redirect('dashboard:dashboard_user')
            if getattr(user, 'empresa', None) != chamado.empresa:
                raise Http404("Chamado não encontrado.")

        context = {
            'chamado': chamado,
            'comentarios': chamado.comentarios.all(),
            'gerado_por': request.user,
            'data_geracao': timezone.now()
        }

        pdf = render_to_pdf('orders/chamado_pdf.html', context)
        if pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = f'inline; filename="OS_{chamado.numero}.pdf"'
            return response

        messages.error(request, "Erro ao gerar PDF.")
        return redirect('chamado_detail', pk=pk)


class EnviarPDFEmailView(LoginRequiredMixin, UserPassesTestMixin, View):
    """ Dispara a tarefa do Celery para enviar o PDF por E-mail """

    def test_func(self):
        return self.request.user.is_staff

    def post(self, request, pk):
        chamado = get_object_or_404(Chamado, pk=pk)

        from .tasks import enviar_pdf_chamado_email_task
        enviar_pdf_chamado_email_task.delay(chamado.id)

        messages.success(request,
                         f"O PDF da O.S. #{chamado.numero} está sendo gerado e será enviado por e-mail em background.")
        return redirect('dashboard:dashboard_admin')


class RelatorioFiltroView(LoginRequiredMixin, UserPassesTestMixin, View):
    """ Página de Relatórios e Exportação Múltipla """

    def test_func(self):
        # Apenas superusers, técnicos ou staff têm acesso
        return self.request.user.is_superuser or getattr(self.request.user, 'is_tecnico',
                                                         False) or self.request.user.is_staff

    def get(self, request):
        # ATUALIZAÇÃO: Adicionado prefetch_related para carregar os comentários e os autores de uma só vez
        qs = Chamado.objects.all().select_related(
            'empresa', 'solicitante', 'tecnico_atribuido', 'categoria'
        ).prefetch_related('comentarios', 'comentarios__autor')

        empresas_disponiveis = None
        user = request.user

        # ==============================================================
        # 1. ISOLAMENTO MULTI-TENANT (IDÊNTICO AO DASHBOARD)
        # ==============================================================
        if getattr(user, 'is_tecnico', False):
            # REGRA 1: Técnico fica restrito às suas empresas vinculadas
            empresas_ids = set()
            if user.empresa_id:
                empresas_ids.add(user.empresa_id)
            if hasattr(user, 'empresas_atendidas'):
                empresas_ids.update(user.empresas_atendidas.values_list('id', flat=True))

            if empresas_ids:
                qs = qs.filter(empresa_id__in=empresas_ids)
                empresas_disponiveis = Empresa.objects.filter(id__in=empresas_ids)
            else:
                qs = qs.none()
                empresas_disponiveis = Empresa.objects.none()

        elif user.is_superuser:
            # REGRA 2: Admin Geral (Não Técnico) vê tudo
            empresas_disponiveis = Empresa.objects.all()

        else:
            # REGRA 3: Staff normal vê apenas a própria empresa
            if user.empresa_id:
                qs = qs.filter(empresa_id=user.empresa_id)
                empresas_disponiveis = Empresa.objects.filter(id=user.empresa_id)
            else:
                qs = qs.none()
                empresas_disponiveis = Empresa.objects.none()
        # ==============================================================

        # 2. Filtros do Formulário (GET)
        empresa_id = request.GET.get('empresa')
        status = request.GET.get('status')
        data_inicio = request.GET.get('data_inicio')
        data_fim = request.GET.get('data_fim')

        if empresa_id:
            qs = qs.filter(empresa_id=empresa_id)
        if status:
            qs = qs.filter(status=status)
        if data_inicio:
            qs = qs.filter(aberto_em__date__gte=data_inicio)
        if data_fim:
            qs = qs.filter(aberto_em__date__lte=data_fim)

        qs = qs.order_by('-aberto_em')

        context = {
            'chamados': qs,
            'empresas': empresas_disponiveis,
            'status_choices': Chamado.STATUS_CHOICES,
            'filtros': request.GET,
            'total_resultados': qs.count(),
            'data_geracao': timezone.now()
        }

        # Se o botão de Exportar for pressionado
        if request.GET.get('export') == 'pdf':
            pdf = render_to_pdf('orders/relatorio_pdf.html', context)
            if pdf:
                response = HttpResponse(pdf, content_type='application/pdf')
                response['Content-Disposition'] = 'attachment; filename="Relatorio_Chamados.pdf"'
                return response
            messages.error(request, "Erro ao gerar PDF do relatório.")

        return render(request, 'orders/relatorio_filtro.html', context)
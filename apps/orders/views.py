from django.views.generic import CreateView, DetailView
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy, reverse, NoReverseMatch
from django.contrib import messages
from .models import Chamado
from .forms import ChamadoForm, ComentarioForm


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 1. Traz todos os comentários vinculados a este chamado
        context['comentarios'] = self.object.comentarios.select_related('autor').all()
        # 2. O SEGREDO ESTÁ AQUI: Enviar o formulário vazio para o template!
        # Sem essa variável 'comentario_form', os campos de texto não aparecem na tela.
        if self.object.status not in ['RESOLVIDO', 'CANCELADO']:
            context['comentario_form'] = ComentarioForm()
        return context


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



class AdicionarComentarioView(LoginRequiredMixin, View):
    def post(self, request, pk):
        chamado = get_object_or_404(Chamado, pk=pk)
        
        # Helper robusto para resolver a URL de redirecionamento 
        # (retorna para a página de onde o usuário veio)
        referer = request.META.get('HTTP_REFERER')
        if referer:
            redirect_url = referer
        else:
            try:
                redirect_url = reverse('orders:chamado_detail', kwargs={'pk': pk})
            except NoReverseMatch:
                try:
                    redirect_url = reverse('chamado_detail', kwargs={'pk': pk})
                except NoReverseMatch:
                    redirect_url = reverse('dashboard:dashboard_user')
        
        # Validação de Segurança
        if not request.user.is_staff and chamado.solicitante != request.user:
            messages.error(request, "Você não tem permissão para interagir com este chamado.")
            return redirect(redirect_url)
            
        # Bloqueio de inserção caso finalizado/cancelado
        if chamado.status in ['RESOLVIDO', 'CANCELADO']:
            messages.error(request, "Este chamado já está encerrado e não aceita novos comentários.")
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
            messages.error(request, "Erro ao adicionar comentário. Verifique se o arquivo enviado é válido.")
            
        return redirect(redirect_url)

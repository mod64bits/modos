from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.views.generic import ListView, CreateView, DetailView, UpdateView
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic.base import View

from apps.core.models import ConfiguracaoGeral
from apps.core.gerador_pdf import render_to_pdf
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, ProtectedError
from decimal import Decimal, InvalidOperation

from .models import Orcamento, ItemProdutoOrcamento, Produto
from .forms import OrcamentoForm, ItemOrcamentoForm, ProdutoForm


# ==========================================
# VIEWS PRINCIPAIS DE ORÇAMENTOS
# ==========================================

class OrcamentoListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Orcamento
    template_name = 'orcamentos/orcamento_list.html'
    context_object_name = 'orcamentos'
    paginate_by = 10  # Define a paginação para exibir 10 resultados por página

    def test_func(self):
        return self.request.user.is_staff

    def get_queryset(self):
        qs = super().get_queryset()

        # Pega nos parâmetros que vêm pela URL (?q=...&status=...)
        query = self.request.GET.get('q')
        status_filter = self.request.GET.get('status')

        # Aplica o filtro de Texto (Busca por Número, Nome Avulso ou Empresa)
        if query:
            qs = qs.filter(
                Q(numero__icontains=query) |
                Q(cliente_avulso_nome__icontains=query) |
                Q(empresa__nome__icontains=query)
            )

        # Aplica o filtro de Status (Se algum for selecionado no dropdown)
        if status_filter:
            qs = qs.filter(status=status_filter)

        # Ordena do mais recente para o mais antigo
        return qs.order_by('-criado_em')


class OrcamentoCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Orcamento
    form_class = OrcamentoForm
    template_name = 'orcamentos/orcamento_form.html'

    def test_func(self):
        return self.request.user.is_staff

    def get_success_url(self):
        # Redireciona logo para a página de detalhes para adicionar produtos
        return reverse_lazy('orcamentos:orcamento_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, "Orçamento criado! Agora adicione os produtos/serviços.")
        return super().form_valid(form)


class OrcamentoUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Orcamento
    form_class = OrcamentoForm
    template_name = 'orcamentos/orcamento_form.html'

    def test_func(self):
        return self.request.user.is_staff

    def get_success_url(self):
        # Após editar, devolve o utilizador à página de detalhes do mesmo orçamento
        return reverse_lazy('orcamentos:orcamento_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, "Orçamento atualizado com sucesso!")
        return super().form_valid(form)


class OrcamentoDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Orcamento
    template_name = 'orcamentos/orcamento_detail.html'
    context_object_name = 'orcamento'

    def test_func(self):
        return self.request.user.is_staff

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # Envia o formulário vazio de adição de itens para o Modal
        ctx['item_form'] = ItemOrcamentoForm()
        ctx['itens'] = self.object.itens.all()
        # Envia as opções de status para o Modal de alteração de status
        ctx['status_choices'] = Orcamento.STATUS_CHOICES
        return ctx

    def post(self, request, *args, **kwargs):
        """ Método acionado quando o formulário de ADICIONAR PRODUTO (Modal) é submetido """
        self.object = self.get_object()
        form = ItemOrcamentoForm(request.POST)

        if form.is_valid():
            item = form.save(commit=False)
            item.orcamento = self.object
            item.save()  # O signal fará o recálculo dos totais automaticamente
            messages.success(request, "Produto adicionado ao orçamento!")
            return redirect('orcamentos:orcamento_detail', pk=self.object.pk)

        # Se houver erro, re-renderiza a página com as mensagens de erro
        ctx = self.get_context_data()
        ctx['item_form'] = form
        messages.error(request, "Erro ao adicionar produto. Verifique os dados.")
        return self.render_to_response(ctx)


# ==========================================
# VIEWS DE AÇÕES RÁPIDAS (MODAIS)
# ==========================================

def atualizar_status_orcamento(request, pk):
    """ View para atualizar rapidamente o status do orçamento via Modal """
    if not request.user.is_staff:
        return JsonResponse({'erro': 'Acesso negado'}, status=403)

    orcamento = get_object_or_404(Orcamento, pk=pk)

    if request.method == 'POST':
        novo_status = request.POST.get('status')
        if novo_status:
            orcamento.status = novo_status
            orcamento.save()
            messages.success(request, "Status do orçamento atualizado com sucesso!")

    return redirect('orcamentos:orcamento_detail', pk=pk)


def deletar_item_orcamento(request, pk):
    """ View para remover um produto do orçamento via Modal """
    if not request.user.is_staff:
        return JsonResponse({'erro': 'Acesso negado'}, status=403)

    item = get_object_or_404(ItemProdutoOrcamento, pk=pk)
    orcamento_id = item.orcamento.id

    if request.method == 'POST':
        item.delete()  # Dispara o signal e reduz o total
        messages.success(request, "Item removido com sucesso.")

    return redirect('orcamentos:orcamento_detail', pk=orcamento_id)


def editar_item_orcamento(request, pk):
    """ View para editar a quantidade e markup de um item via Modal """
    if not request.user.is_staff:
        return JsonResponse({'erro': 'Acesso negado'}, status=403)

    item = get_object_or_404(ItemProdutoOrcamento, pk=pk)
    orcamento_id = item.orcamento.id

    if request.method == 'POST':
        quantidade = request.POST.get('quantidade')
        # Substitui vírgula por ponto para evitar erros de cast em decimais
        markup_str = request.POST.get('porcentagem_markup', '0').replace(',', '.')

        try:
            if quantidade and markup_str:
                item.quantidade = int(quantidade)
                item.porcentagem_markup = Decimal(markup_str)
                item.save()  # Dispara o signal de recálculo dos totais automaticamente
                messages.success(request, "Item atualizado com sucesso!")
        except (ValueError, InvalidOperation):
            messages.error(request, "Valores inválidos. Verifique a quantidade e a margem.")

    return redirect('orcamentos:orcamento_detail', pk=orcamento_id)


# ==========================================
# VIEWS DE API (AJAX / FETCH)
# ==========================================

def api_detalhes_produto(request, pk):
    """ Devolve o preço base de um produto em formato JSON para o JavaScript """
    if not request.user.is_staff:
        return JsonResponse({'erro': 'Acesso negado'}, status=403)

    produto = get_object_or_404(Produto, pk=pk)
    return JsonResponse({
        'id': produto.id,
        'nome': produto.nome,
        'valor_compra': str(produto.valor_compra)
    })


def editar_produto_catalogo(request, pk):
    """ Edita as informações base de um produto do catálogo via Modal """
    if not request.user.is_superuser:
        return JsonResponse({'erro': 'Acesso negado'}, status=403)

    produto = get_object_or_404(Produto, pk=pk)

    if request.method == 'POST':
        produto.nome = request.POST.get('nome')
        produto.fabricante = request.POST.get('fabricante')
        produto.modelo = request.POST.get('modelo')
        produto.link_produto = request.POST.get('link_produto', '')

        valor_str = request.POST.get('valor_compra', '0').replace(',', '.')
        try:
            produto.valor_compra = Decimal(valor_str)
            produto.save()
            messages.success(request, "Produto atualizado no catálogo com sucesso!")
        except (ValueError, InvalidOperation):
            messages.error(request, "Valor de compra inválido.")

    return redirect('orcamentos:produto_list')


def deletar_produto_catalogo(request, pk):
    """ Exclui um produto base do catálogo via Modal, respeitando relacionamentos (Protected) """
    if not request.user.is_superuser:
        return JsonResponse({'erro': 'Acesso negado'}, status=403)

    produto = get_object_or_404(Produto, pk=pk)

    if request.method == 'POST':
        try:
            produto.delete()
            messages.success(request, "Produto removido do catálogo com sucesso!")
        except ProtectedError:
            # Protege o sistema de dar erro (crash 500) caso este produto esteja nalgum orçamento salvo!
            messages.error(request,
                           "Erro: Este produto não pode ser excluído pois já está vinculado a um ou mais orçamentos.")

    return redirect('orcamentos:produto_list')


# ==========================================
# VIEWS DE PRODUTOS (CATÁLOGO - APENAS ADMIN)
# ==========================================

class ProdutoListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Produto
    template_name = 'orcamentos/produto_list.html'
    context_object_name = 'produtos'
    paginate_by = 10  # Paginação
    ordering = ['-criado_em']  # Ordenação padrão necessária para o Paginator funcionar

    def test_func(self):
        # Somente administradores gerais podem ver o catálogo de produtos e os preços base
        return self.request.user.is_superuser


class ProdutoCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Produto
    form_class = ProdutoForm
    template_name = 'orcamentos/produto_form.html'
    success_url = reverse_lazy('orcamentos:produto_list')

    def test_func(self):
        # Somente administradores gerais podem adicionar novos produtos
        return self.request.user.is_superuser

    def form_valid(self, form):
        messages.success(self.request, "Produto cadastrado no catálogo com sucesso!")
        return super().form_valid(form)


class OrcamentoPDFClienteView(LoginRequiredMixin, DetailView):
    """ Gera o PDF apenas com valores de VENDA para enviar ao cliente """
    model = Orcamento

    def get(self, request, *args, **kwargs):
        orcamento = self.get_object()
        config = ConfiguracaoGeral.load()

        context = {
            'orcamento': orcamento,
            'itens': orcamento.itens.all(),
            'minha_empresa': config,
            'tipo_pdf': 'cliente'
        }

        pdf = render_to_pdf('orcamentos/pdfs/orcamento_pdf_cliente.html', context)
        if pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            # 'inline' faz abrir na aba. 'attachment' faria download.
            response['Content-Disposition'] = f'inline; filename="Orcamento_{orcamento.numero}.pdf"'
            return response
        return HttpResponse("Erro ao gerar o PDF.", status=500)


class OrcamentoPDFInternoView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """ Gera o PDF com Lucros e Custos (Acesso restrito a técnicos) """
    model = Orcamento

    def test_func(self):
        return self.request.user.is_staff

    def get(self, request, *args, **kwargs):
        orcamento = self.get_object()

        try:
            config = ConfiguracaoGeral.objects.first()
        except Exception:
            config = None

        context = {
            'orcamento': orcamento,
            'itens': orcamento.itens.all(),
            'minha_empresa': config,
            'tipo_pdf': 'interno',
            'gerado_por': request.user
        }

        pdf = render_to_pdf('orcamentos/pdfs/orcamento_pdf_interno.html', context)
        if pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = f'inline; filename="Orcamento_{orcamento.numero}_INTERNO.pdf"'
            return response
        return HttpResponse("Erro ao gerar o PDF.", status=500)


class PublicOrcamentoPDFView(View):
    """ Gera o PDF para o cliente se a validade não estiver expirada """

    def get(self, request, numero, hash_acesso):
        # 1. Tenta encontrar o orçamento pela combinação exata de Número + Hash
        orcamento = get_object_or_404(Orcamento, numero=numero, hash_acesso=hash_acesso.upper())

        # 2. VERIFICAÇÃO DE VALIDADE
        hoje = timezone.now().date()
        if orcamento.validade < hoje:
            # Se expirou, renderiza a página de erro (o HTML que tem no Canvas)
            context_erro = {'orcamento': orcamento}
            return render(request, 'orcamentos/public_expirado.html', context_erro)

        # 3. Se estiver válido, carrega as configurações e gera o PDF da Via do Cliente
        try:
            config = ConfiguracaoGeral.objects.first()
        except Exception:
            config = None

        context = {
            'orcamento': orcamento,
            'itens': orcamento.itens.all(),
            'minha_empresa': config,
            'tipo_pdf': 'cliente'
        }

        pdf = render_to_pdf('orcamentos/pdfs/orcamento_pdf_cliente.html', context)

        if pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            # 'inline' faz o PDF abrir diretamente num novo separador do navegador
            response['Content-Disposition'] = f'inline; filename="Orcamento_{orcamento.numero}.pdf"'
            return response

        return HttpResponse("Ocorreu um erro ao processar o seu documento.", status=500)


class PublicOrcamentoConsultaView(View):
    """ Exibe a página para o cliente inserir o Número e a Hash """

    def get(self, request):
        # Quando o cliente acede ao link, mostramos a tela limpa de formulário
        return render(request, 'orcamentos/public_consulta.html')

    def post(self, request):
        # Quando o cliente clica em "Aceder ao Documento"
        numero = request.POST.get('numero')
        hash_acesso = request.POST.get('hash_acesso', '').strip().upper()

        try:
            # Verifica na base de dados se existe um orçamento com a combinação exata
            orcamento = Orcamento.objects.get(numero=numero, hash_acesso=hash_acesso)

            # Se encontrar, redireciona o utilizador para a View do PDF passando os dados na URL
            return redirect('orcamentos:pdf_publico', numero=orcamento.numero, hash_acesso=orcamento.hash_acesso)

        except Orcamento.DoesNotExist:
            # Se a combinação estiver errada, devolve um erro na mesma tela
            messages.error(request, "Orçamento não encontrado ou código de acesso inválido.")
            return redirect('orcamentos:consulta_publica')
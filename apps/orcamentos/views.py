from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.http import JsonResponse

from .models import Orcamento, ItemProdutoOrcamento, Produto
from .forms import OrcamentoForm, ItemOrcamentoForm, ProdutoForm


class OrcamentoListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Orcamento
    template_name = 'orcamentos/orcamento_list.html'
    context_object_name = 'orcamentos'

    def test_func(self):
        return self.request.user.is_staff


class OrcamentoCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Orcamento
    form_class = OrcamentoForm
    template_name = 'orcamentos/orcamento_form.html'

    def test_func(self):
        return self.request.user.is_staff

    def get_success_url(self):
        return reverse_lazy('orcamentos:orcamento_detail', kwargs={'pk': self.object.pk})


class OrcamentoDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Orcamento
    template_name = 'orcamentos/orcamento_detail.html'
    context_object_name = 'orcamento'

    def test_func(self):
        return self.request.user.is_staff

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['item_form'] = ItemOrcamentoForm()
        ctx['itens'] = self.object.itens.all()
        ctx['status_choices'] = Orcamento.STATUS_CHOICES  # NOVO: Envia as opções de status para o modal
        return ctx

    def post(self, request, *args, **kwargs):
        """ Adiciona um novo Item ao Orçamento ao submeter o Modal """
        self.object = self.get_object()
        form = ItemOrcamentoForm(request.POST)

        if form.is_valid():
            item = form.save(commit=False)
            item.orcamento = self.object
            item.save()  # Isso dispara o signal que atualiza os totais automaticamente
            messages.success(request, "Produto adicionado com sucesso!")
        else:
            messages.error(request, "Erro ao adicionar produto. Verifique os dados.")

        return redirect('orcamentos:orcamento_detail', pk=self.object.pk)


def deletar_item_orcamento(request, pk):
    """ View para remover um produto do orçamento """
    if not request.user.is_staff:
        return JsonResponse({'erro': 'Acesso negado'}, status=403)

    item = get_object_or_404(ItemProdutoOrcamento, pk=pk)
    orcamento_id = item.orcamento.id

    # Adicionamos segurança: a exclusão só ocorre por POST (vinda do form do modal)
    if request.method == 'POST':
        item.delete()  # Dispara o signal e reduz o total
        messages.success(request, "Item removido com sucesso.")

    return redirect('orcamentos:orcamento_detail', pk=orcamento_id)


def editar_item_orcamento(request, pk):
    """ View para editar a quantidade e markup de um item via Modal """
    from decimal import Decimal, InvalidOperation

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
            messages.success(request, f"Status do orçamento atualizado com sucesso!")

    return redirect('orcamentos:orcamento_detail', pk=pk)


def api_detalhes_produto(request, pk):
    if not request.user.is_staff:
        return JsonResponse({'erro': 'Acesso negado'}, status=403)

    produto = get_object_or_404(Produto, pk=pk)
    return JsonResponse({
        'id': produto.id,
        'nome': produto.nome,
        'valor_compra': str(produto.valor_compra)
    })


# ==========================================
# VIEWS DE PRODUTOS (APENAS ADMIN)
# ==========================================
class ProdutoListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Produto
    template_name = 'orcamentos/produto_list.html'
    context_object_name = 'produtos'

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
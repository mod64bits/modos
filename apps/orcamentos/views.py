from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.http import JsonResponse

from .models import Orcamento, ItemProdutoOrcamento, Produto
from .forms import OrcamentoForm, ItemOrcamentoForm


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
        return reverse_lazy('orcamento_detail', kwargs={'pk': self.object.pk})


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

        return redirect('orcamento_detail', pk=self.object.pk)


def deletar_item_orcamento(request, pk):
    """ View para remover um produto do orçamento """
    if not request.user.is_staff:
        return JsonResponse({'erro': 'Acesso negado'}, status=403)

    item = get_object_or_404(ItemProdutoOrcamento, pk=pk)
    orcamento_id = item.orcamento.id
    item.delete()  # Dispara o signal e reduz o total
    messages.success(request, "Item removido com sucesso.")
    return redirect('orcamento_detail', pk=orcamento_id)


def api_detalhes_produto(request, pk):
    """ API simples para o Javascript do Modal buscar o preço de compra em tempo real """
    if not request.user.is_staff:
        return JsonResponse({'erro': 'Acesso negado'}, status=403)

    produto = get_object_or_404(Produto, pk=pk)
    return JsonResponse({
        'id': produto.id,
        'nome': produto.nome,
        'valor_compra': str(produto.valor_compra)
    })
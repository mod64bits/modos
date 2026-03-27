from django import forms
from django.core.exceptions import ValidationError
from .models import Orcamento, ItemProdutoOrcamento, Produto

default_attrs = {
    'class': 'mt-1 block w-full py-2 px-3 border border-gray-300 bg-white rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 sm:text-sm'
}

class OrcamentoForm(forms.ModelForm):
    class Meta:
        model = Orcamento
        fields = ['empresa', 'cliente_avulso_nome', 'cliente_avulso_contato', 'validade', 'status', 'descricao_geral', 'total_mao_de_obra', 'total_insumos']
        widgets = {
            'empresa': forms.Select(attrs=default_attrs),
            'cliente_avulso_nome': forms.TextInput(attrs=default_attrs),
            'cliente_avulso_contato': forms.TextInput(attrs=default_attrs),
            'validade': forms.DateInput(attrs={'type': 'date', 'class': default_attrs['class']}),
            'status': forms.Select(attrs=default_attrs),
            'descricao_geral': forms.Textarea(attrs={'class': default_attrs['class'], 'rows': 3}),
            'total_mao_de_obra': forms.NumberInput(attrs=default_attrs),
            'total_insumos': forms.NumberInput(attrs=default_attrs),
        }

    def clean(self):
        cleaned_data = super().clean()
        empresa = cleaned_data.get("empresa")
        avulso = cleaned_data.get("cliente_avulso_nome")

        if not empresa and not avulso:
            raise ValidationError("Você deve selecionar uma Empresa cadastrada OU informar o Nome do Cliente Avulso.")
        return cleaned_data

class ItemOrcamentoForm(forms.ModelForm):
    class Meta:
        model = ItemProdutoOrcamento
        fields = ['produto', 'quantidade', 'porcentagem_markup']
        widgets = {
            'produto': forms.Select(attrs=default_attrs),
            'quantidade': forms.NumberInput(attrs=default_attrs),
            'porcentagem_markup': forms.NumberInput(attrs=default_attrs),
        }


class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produto
        fields = ['nome', 'fabricante', 'modelo', 'descricao', 'valor_compra', 'link_produto']
        widgets = {
            'nome': forms.TextInput(attrs=default_attrs),
            'fabricante': forms.TextInput(attrs=default_attrs),
            'modelo': forms.TextInput(attrs=default_attrs),
            'descricao': forms.Textarea(attrs={'class': default_attrs['class'], 'rows': 3}),
            'valor_compra': forms.NumberInput(attrs=default_attrs),
            'link_produto': forms.URLInput(attrs=default_attrs),
        }
from django import forms
from apps.companies.models import Empresa
from apps.equipment.models import Equipamento
from apps.orders.models import CategoriaServico

# Classe CSS padrão para manter o design do Tailwind
default_attrs = {
    'class': 'mt-1 block w-full py-2 px-3 border border-gray-300 bg-white rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'
}


class EmpresaForm(forms.ModelForm):
    class Meta:
        model = Empresa
        fields = ['nome', 'cnpj', 'email', 'telefone_responsavel']
        widgets = {
            'nome': forms.TextInput(attrs=default_attrs),
            'cnpj': forms.TextInput(attrs=default_attrs),
            'email': forms.EmailInput(attrs=default_attrs),
            'telefone_responsavel': forms.TextInput(attrs=default_attrs),
        }


class EquipamentoForm(forms.ModelForm):
    class Meta:
        model = Equipamento
        fields = ['empresa', 'nome', 'marca', 'modelo', 'serial']
        widgets = {
            'empresa': forms.Select(attrs=default_attrs),
            'nome': forms.TextInput(attrs=default_attrs),
            'marca': forms.TextInput(attrs=default_attrs),
            'modelo': forms.TextInput(attrs=default_attrs),
            'serial': forms.TextInput(attrs=default_attrs),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Inteligência de Multi-Tenant no formulário de Equipamento
        if user:
            if user.is_superuser:
                pass  # Admin vê tudo
            elif getattr(user, 'is_tecnico', False):
                empresas_ids = set()
                if user.empresa_id:
                    empresas_ids.add(user.empresa_id)
                if hasattr(user, 'empresas_atendidas'):
                    empresas_ids.update(user.empresas_atendidas.values_list('id', flat=True))
                # Limita as empresas disponíveis no Dropdown
                self.fields['empresa'].queryset = Empresa.objects.filter(id__in=empresas_ids)


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = CategoriaServico
        fields = ['nome', 'descricao']
        widgets = {
            'nome': forms.TextInput(attrs=default_attrs),
            'descricao': forms.Textarea(attrs={'class': default_attrs['class'], 'rows': 3}),
        }
from django import forms
from .models import Chamado
from apps.equipment.models import Equipamento # Ajuste o import conforme seu app de equipamentos

class ChamadoForm(forms.ModelForm):
    class Meta:
        model = Chamado
        fields = ['titulo', 'tipo', 'categoria', 'setor', 'equipamento', 'prioridade', 'descricao']
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md',
                'placeholder': 'Ex: Computador não liga'
            }),
            'tipo': forms.Select(attrs={
                'class': 'mt-1 block w-full py-2 px-3 border border-gray-300 bg-white rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'
            }),
            'categoria': forms.Select(attrs={
                'class': 'mt-1 block w-full py-2 px-3 border border-gray-300 bg-white rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'
            }),
            'setor': forms.Select(attrs={
                'class': 'mt-1 block w-full py-2 px-3 border border-gray-300 bg-white rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'
            }),
            'equipamento': forms.Select(attrs={
                'class': 'mt-1 block w-full py-2 px-3 border border-gray-300 bg-white rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'
            }),
            'prioridade': forms.Select(attrs={
                'class': 'mt-1 block w-full py-2 px-3 border border-gray-300 bg-white rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md',
                'rows': 4,
                'placeholder': 'Descreva detalhadamente o problema ou solicitação...'
            }),
        }

    def __init__(self, *args, **kwargs):
        # Recebe o usuário logado para filtrar os equipamentos
        user = kwargs.pop('user', None)
        super(ChamadoForm, self).__init__(*args, **kwargs)
        
        if user and user.empresa:
            # Filtra equipamentos para mostrar APENAS os da empresa do usuário
            self.fields['equipamento'].queryset = Equipamento.objects.filter(empresa=user.empresa)
            # Opcional: Filtrar setores da empresa
            # self.fields['setor'].queryset = Setor.objects.filter(empresa=user.empresa)
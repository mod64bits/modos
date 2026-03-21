from django import forms
from .models import Chamado, Comentario
from apps.equipment.models import Equipamento
from apps.accounts.models import Usuario  # Adicionado
from apps.companies.models import Empresa, Setor


class ChamadoForm(forms.ModelForm):
    class Meta:
        model = Chamado
        # Adicionados os campos 'empresa' e 'solicitante'
        fields = ['empresa', 'solicitante', 'titulo', 'tipo', 'prioridade', 'categoria', 'setor', 'equipamento',
                  'descricao']
        widgets = {
            'empresa': forms.Select(attrs={
                'class': 'mt-1 block w-full py-2 px-3 border border-gray-300 bg-white rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'
            }),
            'solicitante': forms.Select(attrs={
                'class': 'mt-1 block w-full py-2 px-3 border border-gray-300 bg-white rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'
            }),
            'titulo': forms.TextInput(attrs={
                'class': 'mt-1 focus:ring-indigo-500 focus:border-indigo-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md'
            }),
            'tipo': forms.Select(attrs={
                'class': 'mt-1 block w-full py-2 px-3 border border-gray-300 bg-white rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'
            }),
            'prioridade': forms.Select(attrs={
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
            'descricao': forms.Textarea(attrs={
                'rows': 4,
                'class': 'shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border border-gray-300 rounded-md'
            }),
        }

    def __init__(self, *args, **kwargs):
        # Captura o utilizador logado passado pela View
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user:
            # 1. ADMINS E TÉCNICOS
            if user.is_staff:
                if user.is_superuser:
                    # Admin Geral: Vê todas as empresas e todos os utilizadores
                    pass
                elif getattr(user, 'is_tecnico', False):
                    # Técnico: Vê apenas as empresas vinculadas a ele
                    empresas_ids = set()
                    if user.empresa_id:
                        empresas_ids.add(user.empresa_id)
                    if hasattr(user, 'empresas_atendidas'):
                        empresas_ids.update(user.empresas_atendidas.values_list('id', flat=True))

                    self.fields['empresa'].queryset = Empresa.objects.filter(id__in=empresas_ids)
                    self.fields['solicitante'].queryset = Usuario.objects.filter(empresa_id__in=empresas_ids)
                    self.fields['setor'].queryset = Setor.objects.filter(empresa_id__in=empresas_ids)
                    self.fields['equipamento'].queryset = Equipamento.objects.filter(empresa_id__in=empresas_ids)

            # 2. CLIENTE COMUM (Remove os campos para que o cliente não os veja nem altere)
            else:
                if 'empresa' in self.fields:
                    del self.fields['empresa']
                if 'solicitante' in self.fields:
                    del self.fields['solicitante']

                if getattr(user, 'empresa', None):
                    self.fields['equipamento'].queryset = Equipamento.objects.filter(empresa=user.empresa)
                    self.fields['setor'].queryset = user.empresa.setores.all()


class ComentarioForm(forms.ModelForm):
    class Meta:
        model = Comentario
        fields = ['texto', 'anexo']
        widgets = {
            'texto': forms.Textarea(attrs={
                'class': 'shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md',
                'rows': 3,
                'placeholder': 'Escreva o seu comentário aqui...'
            }),
            'anexo': forms.ClearableFileInput(attrs={
                'class': 'mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100'
            })
        }
        labels = {
            'texto': '',  # Ocultamos a label de texto para ficar mais limpo
            'anexo': ''  # A label já está desenhada no HTML
        }
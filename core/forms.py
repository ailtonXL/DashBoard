from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from .models import Atestado, HorimetroRegistro


class AtestadoForm(forms.ModelForm):
    class Meta:
        model = Atestado
        fields = [
            'nome',
            'empresa',
            'tipo',
            'data_inicio',
            'hora_saida',
            'data_fim',
            'hora_retorno',
            'classificacao',
            'medico',
            'crm_cro_cress',
            'uf',
            'arquivo',
        ]
        labels = {
            'nome': 'Nome',
            'empresa': 'Empresa',
            'tipo': 'Tipo',
            'data_inicio': 'Data Início',
            'hora_saida': 'Hora Saída',
            'data_fim': 'Data Fim',
            'hora_retorno': 'Hora Retorno',
            'classificacao': 'Classificação',
            'uf': 'UF',
            'medico': 'Médico',
            'crm_cro_cress': 'CRM / CRO / CRESS (apenas números)',
            'arquivo': 'Arquivo',
        }
        widgets = {
            'tipo': forms.Select(attrs={'class': 'campo-tipo'}),
            'uf': forms.Select(attrs={'class': 'campo-tipo'}),
            'data_inicio': forms.DateInput(attrs={'type': 'date'}),
            'data_fim': forms.DateInput(attrs={'type': 'date'}),
            'hora_saida': forms.TimeInput(attrs={'type': 'time'}),
            'hora_retorno': forms.TimeInput(attrs={'type': 'time'}),
            'crm_cro_cress': forms.TextInput(attrs={'inputmode': 'numeric', 'pattern': '[0-9]*', 'placeholder': 'Ex: 12345'}),
        }

    def clean_crm_cro_cress(self):
        valor = self.cleaned_data.get('crm_cro_cress', '')
        if valor and not valor.isdigit():
            raise forms.ValidationError('Este campo aceita apenas números.')
        return valor


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label='Usuário',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Digite seu usuário'})
    )
    password = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Digite sua senha'})
    )


class HorimetroRegistroForm(forms.ModelForm):
    class Meta:
        model = HorimetroRegistro
        fields = ['tipo_registro', 'veiculo', 'maquinario', 'placa', 'data_registro', 'quilometragem', 'horimetro']
        labels = {
            'tipo_registro': 'Tipo',
            'veiculo': 'Veiculo',
            'maquinario': 'Maquinario',
            'placa': 'Placa',
            'data_registro': 'Data',
            'quilometragem': 'Quilometragem',
            'horimetro': 'Horimetro',
        }
        widgets = {
            'tipo_registro': forms.Select(),
            'veiculo': forms.TextInput(attrs={'placeholder': 'Informe o nome ou identificacao do veiculo'}),
            'maquinario': forms.TextInput(attrs={'placeholder': 'Informe o nome do maquinario'}),
            'placa': forms.TextInput(attrs={'placeholder': 'ABC1D23', 'maxlength': '8'}),
            'data_registro': forms.DateInput(attrs={'type': 'date'}),
            'quilometragem': forms.NumberInput(attrs={'min': '0', 'step': '0.1', 'placeholder': 'Informe a quilometragem atual'}),
            'horimetro': forms.NumberInput(attrs={'min': '0', 'step': '0.1', 'placeholder': 'Informe o horimetro atual'}),
        }

    def clean_placa(self):
        placa = (self.cleaned_data.get('placa') or '').upper().replace('-', '').replace(' ', '')
        tipo_registro = self.cleaned_data.get('tipo_registro')
        if tipo_registro == 'maquina':
            return ''
        if len(placa) not in {7, 8}:
            raise forms.ValidationError('Informe uma placa valida.')
        return placa

    def clean(self):
        cleaned_data = super().clean()
        tipo_registro = cleaned_data.get('tipo_registro')

        if tipo_registro == 'maquina':
            if not cleaned_data.get('maquinario'):
                self.add_error('maquinario', 'Informe o nome do maquinario.')
            if cleaned_data.get('horimetro') in (None, ''):
                self.add_error('horimetro', 'Informe o horimetro.')

            cleaned_data['veiculo'] = ''
            cleaned_data['placa'] = ''
            cleaned_data['quilometragem'] = None
        else:
            if not cleaned_data.get('veiculo'):
                self.add_error('veiculo', 'Informe o nome do veiculo.')
            if cleaned_data.get('quilometragem') in (None, ''):
                self.add_error('quilometragem', 'Informe a quilometragem.')

            cleaned_data['maquinario'] = ''
            cleaned_data['horimetro'] = None

        return cleaned_data

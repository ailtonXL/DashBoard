from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from .models import Atestado


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
            'medico': 'Médico',
            'crm_cro_cress': 'CRM / CRO / CRESS',
            'arquivo': 'Arquivo',
        }
        widgets = {
            'tipo': forms.Select(attrs={'class': 'campo-tipo'}),
            'data_inicio': forms.DateInput(attrs={'type': 'date'}),
            'data_fim': forms.DateInput(attrs={'type': 'date'}),
            'hora_saida': forms.TimeInput(attrs={'type': 'time'}),
            'hora_retorno': forms.TimeInput(attrs={'type': 'time'}),
        }


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label='Usuário',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Digite seu usuário'})
    )
    password = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Digite sua senha'})
    )

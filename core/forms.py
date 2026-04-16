from django import forms
from .models import Atestado


class AtestadoForm(forms.ModelForm):
    class Meta:
        model = Atestado
        fields = ['nome', 'data_inicio', 'data_fim', 'arquivo']
# formulário
from django import forms

from .models import Membro  # type: ignore


class MembroForm(forms.ModelForm):
    """
    Formulário de cadastro/edição de Membro.
    Usa os campos do model diretamente e aplica classes do Bootstrap
    em cada widget para ficar bonito sem precisar de django-crispy-forms.
    """

    class Meta:
        model = Membro
        fields = ['nome_completo', 'email', 'telefone', 'status', 'tipo_membro']  # noqa: RUF012
        widgets = {  # noqa: RUF012
            'nome_completo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Digite o nome completo',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'exemplo@email.com',
            }),
            'telefone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '(00) 00000-0000',
            }),
            'status': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
            'tipo_membro': forms.Select(attrs={
                'class': 'form-select',
            }),
        }

    def clean_telefone(self):
        """Remove espaços extras do telefone, se informado."""
        telefone = self.cleaned_data.get('telefone')
        if telefone:
            telefone = telefone.strip()
        return telefone

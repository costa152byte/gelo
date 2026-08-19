# formulários do sistema Artgelo
from django import forms
from django.forms import inlineformset_factory
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit

from .models import Membro, Pedido, ItemPedido, Rota, AgendamentoLimpeza, Endereco


class MembroForm(forms.ModelForm):
    class Meta:
        model = Membro
        fields = ['nome_completo', 'email', 'telefone', 'status', 'tipo_membro']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('nome_completo', css_class='col-md-6'),
                Column('email', css_class='col-md-6'),
            ),
            Row(
                Column('telefone', css_class='col-md-4'),
                Column('tipo_membro', css_class='col-md-4'),
                Column('status', css_class='col-md-4 pt-4'),
            ),
            Submit('submit', 'Salvar', css_class='btn btn-primary'),
        )


class EnderecoForm(forms.ModelForm):
    class Meta:
        model = Endereco
        fields = ['rua', 'numero', 'bairro', 'cidade', 'cep', 'principal']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Row(
                Column('rua', css_class='col-md-8'),
                Column('numero', css_class='col-md-4'),
            ),
            Row(
                Column('bairro', css_class='col-md-4'),
                Column('cidade', css_class='col-md-4'),
                Column('cep', css_class='col-md-4'),
            ),
            'principal',
        )


class PedidoForm(forms.ModelForm):
    """
    form_tag=False de propósito: este form é combinado com o
    ItemPedidoFormSet dentro de um único <form> no template
    (pedido_form.html), então quem desenha o <form> e o botão
    de salvar é o template, não o crispy.
    """
    class Meta:
        model = Pedido
        fields = ['cliente', 'endereco_entrega', 'data_entrega', 'status', 'observacoes']
        widgets = {
            'data_entrega': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'observacoes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['data_entrega'].input_formats = ['%Y-%m-%dT%H:%M']

        if self.instance.pk and self.instance.cliente_id:
            self.fields['endereco_entrega'].queryset = Endereco.objects.filter(membro=self.instance.cliente)
        elif 'cliente' in self.data:
            try:
                cliente_id = int(self.data.get('cliente'))
                self.fields['endereco_entrega'].queryset = Endereco.objects.filter(membro_id=cliente_id)
            except (ValueError, TypeError):
                pass

        self.helper = FormHelper()
        self.helper.form_tag = False  # o <form> é escrito no template, junto com o formset
        self.helper.layout = Layout(
            Row(
                Column('cliente', css_class='col-md-6'),
                Column('endereco_entrega', css_class='col-md-6'),
            ),
            Row(
                Column('data_entrega', css_class='col-md-6'),
                Column('status', css_class='col-md-6'),
            ),
            'observacoes',
        )


class ItemPedidoForm(forms.ModelForm):
    class Meta:
        model = ItemPedido
        fields = ['produto', 'quantidade']
        widgets = {
            'produto': forms.Select(attrs={'class': 'form-select'}),
            'quantidade': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'}),
        }


ItemPedidoFormSet = inlineformset_factory(
    Pedido,
    ItemPedido,
    form=ItemPedidoForm,
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True,
)


class RotaForm(forms.ModelForm):
    class Meta:
        model = Rota
        fields = ['nome', 'data', 'motorista', 'status', 'pedidos']
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date'}),
            'pedidos': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['pedidos'].queryset = Pedido.objects.filter(status__in=['confirmado', 'pendente'])
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('nome', css_class='col-md-6'),
                Column('data', css_class='col-md-6'),
            ),
            Row(
                Column('motorista', css_class='col-md-6'),
                Column('status', css_class='col-md-6'),
            ),
            'pedidos',
            Submit('submit', 'Salvar Rota', css_class='btn btn-primary'),
        )


class AgendamentoLimpezaForm(forms.ModelForm):
    class Meta:
        model = AgendamentoLimpeza
        fields = ['nome_cliente', 'telefone', 'endereco', 'data_hora', 'tipo_freezer', 'observacoes']
        widgets = {
            'data_hora': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'observacoes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['data_hora'].input_formats = ['%Y-%m-%dT%H:%M']
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('nome_cliente', css_class='col-md-6'),
                Column('telefone', css_class='col-md-6'),
            ),
            'endereco',
            Row(
                Column('data_hora', css_class='col-md-6'),
                Column('tipo_freezer', css_class='col-md-6'),
            ),
            'observacoes',
            Submit('submit', 'Agendar Limpeza', css_class='btn btn-primary'),
        )

    def clean_data_hora(self):
        data_hora = self.cleaned_data['data_hora']
        if data_hora.weekday() == 6:
            raise forms.ValidationError("Não realizamos agendamentos aos domingos.")
        if not (8 <= data_hora.hour < 18):
            raise forms.ValidationError("Escolha um horário entre 08:00 e 18:00.")
        return data_hora


class FiltroPedidoForm(forms.Form):
    """Formulário de busca/filtro usado na listagem de pedidos."""
    STATUS_CHOICES = [('', 'Todos os status')] + Pedido.STATUS_CHOICES

    busca = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Buscar por cliente...'}),
    )
    status = forms.ChoiceField(choices=STATUS_CHOICES, required=False)
    data_inicio = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    data_fim = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'get'
        self.helper.layout = Layout(
            Row(
                Column('busca', css_class='col-md-4'),
                Column('status', css_class='col-md-2'),
                Column('data_inicio', css_class='col-md-2'),
                Column('data_fim', css_class='col-md-2'),
                Column(
                    Submit('submit', 'Filtrar', css_class='btn btn-outline-secondary w-100 mt-4'),
                    css_class='col-md-2',
                ),
            )
        )
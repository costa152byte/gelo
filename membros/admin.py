"""
Registro no Django Admin do sistema de pedidos da Artgelo.
Cole este conteúdo no admin.py do app (junto com o que já existe para Membro).
"""

from django.contrib import admin

from .models import AgendamentoLimpeza, Endereco, ItemPedido, Pedido, Produto, Rota


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'preco_kg', 'disponivel')
    list_filter = ('disponivel',)
    search_fields = ('nome',)
    list_editable = ('disponivel', 'preco_kg')


@admin.register(Endereco)
class EnderecoAdmin(admin.ModelAdmin):
    list_display = ('membro', 'rua', 'bairro', 'cidade', 'principal')
    list_filter = ('cidade', 'principal')
    search_fields = ('rua', 'bairro', 'cidade', 'cep', 'membro__nome_completo')
    autocomplete_fields = ('membro',)


class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    extra = 1
    readonly_fields = ('subtotal',)
    autocomplete_fields = ('produto',)


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'status', 'data_entrega', 'valor_total', 'rota')
    list_filter = ('status', 'data_entrega', 'rota')
    search_fields = ('cliente__nome_completo', 'id')
    readonly_fields = ('valor_total', 'data_pedido')
    date_hierarchy = 'data_entrega'
    inlines = [ItemPedidoInline]  # noqa: RUF012
    autocomplete_fields = ('cliente', 'endereco_entrega', 'rota')

    actions = ['marcar_confirmado', 'marcar_em_rota', 'marcar_entregue']  # noqa: RUF012

    @admin.action(description="Marcar selecionados como Confirmado")
    def marcar_confirmado(self, request, queryset):
        queryset.update(status='confirmado')

    @admin.action(description="Marcar selecionados como Em Rota")
    def marcar_em_rota(self, request, queryset):
        queryset.update(status='em_rota')

    @admin.action(description="Marcar selecionados como Entregue")
    def marcar_entregue(self, request, queryset):
        queryset.update(status='entregue')


@admin.register(Rota)
class RotaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'data', 'motorista', 'status', 'total_entregas', 'distancia_total')
    list_filter = ('status', 'data')
    search_fields = ('nome', 'motorista')
    filter_horizontal = ('pedidos',)


@admin.register(AgendamentoLimpeza)
class AgendamentoLimpezaAdmin(admin.ModelAdmin):
    list_display = ('nome_cliente', 'telefone', 'data_hora', 'tipo_freezer', 'confirmado')
    list_filter = ('confirmado', 'tipo_freezer', 'data_hora')
    search_fields = ('nome_cliente', 'telefone')
    date_hierarchy = 'data_hora'
    actions = ['confirmar_agendamentos']  # noqa: RUF012

    @admin.action(description="Confirmar agendamentos selecionados")
    def confirmar_agendamentos(self, request, queryset):
        queryset.update(confirmado=True)
# views.py
import json  # noqa: F401
from datetime import datetime, timedelta  # noqa: F401

import requests  # type: ignore # noqa: F401
from django.contrib import messages  # pyright: ignore[reportMissingModuleSource]
from django.contrib.auth.decorators import login_required  # type: ignore
from django.contrib.auth.mixins import LoginRequiredMixin  # type: ignore # noqa: F401
from django.db.models import (  # pyright: ignore[reportMissingModuleSource] # noqa: F401
    Count,
    F,
    Q,
    Sum,
)
from django.http import JsonResponse  # type: ignore
from django.shortcuts import (  # pyright: ignore[reportMissingModuleSource]
    get_object_or_404,
    redirect,
    render,
)
from django.urls import (  # pyright: ignore[reportMissingModuleSource] # noqa: F401
    reverse,
    reverse_lazy,
)
from django.utils import timezone  # pyright: ignore[reportMissingModuleSource]
from django.views.generic import (  # type: ignore
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from .forms import (
    AgendamentoLimpezaForm,
    EnderecoForm,
    FiltroPedidoForm,
    ItemPedidoFormSet,
    MembroForm,
    PedidoForm,
    RotaForm,
)
from .models import (
    AgendamentoLimpeza,
    Endereco,
    ItemPedido,
    Membro,
    Pedido,
    Produto,
    Rota,
)

# ============= VIEWS DE MEMBROS (EXISTENTES) =============

class MembroListView(ListView):
    model = Membro
    template_name = 'membros/listar_membro.html'
    context_object_name = 'membros'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        busca = self.request.GET.get('busca')
        if busca:
            queryset = queryset.filter(nome_completo__icontains=busca)
        status = self.request.GET.get('status')
        if status == 'ativo':
            queryset = queryset.filter(status=True)
        elif status == 'inativo':
            queryset = queryset.filter(status=False)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['busca'] = self.request.GET.get('busca', '')
        context['status_filtro'] = self.request.GET.get('status', '')
        return context

class MembroCreateView(CreateView):
    model = Membro
    form_class = MembroForm
    template_name = 'membros/criar_membro.html'
    success_url = reverse_lazy('membros:listar_membro')
    success_message = "Membro '%(nome_completo)s' cadastrado com sucesso!"

class MembroUpdateView(UpdateView):
    model = Membro
    form_class = MembroForm
    template_name = 'membros/editar_membro.html'
    success_url = reverse_lazy('membros:listar_membro')
    success_message = "Membro '%(nome_completo)s' atualizado com sucesso!"

class MembroDeleteView(DeleteView):
    model = Membro
    template_name = 'membros/confirmar_deleção.html'
    success_url = reverse_lazy('membros:listar_membro')

# ============= VIEWS DE PRODUTOS =============

class ProdutoListView(ListView):
    model = Produto
    template_name = 'produtos/listar_produtos.html'
    context_object_name = 'produtos'
    paginate_by = 12

    def get_queryset(self):
        queryset = Produto.objects.filter(disponivel=True)
        busca = self.request.GET.get('busca')
        if busca:
            queryset = queryset.filter(Q(nome__icontains=busca) | Q(descricao__icontains=busca))
        return queryset

# ============= VIEWS DE ENDEREÇOS =============

@login_required
def endereco_create(request, membro_id=None):
    """View para criar endereço para um membro"""
    membro = None
    if membro_id:
        membro = get_object_or_404(Membro, pk=membro_id)
    
    if request.method == 'POST':
        form = EnderecoForm(request.POST)
        if form.is_valid():
            endereco = form.save(commit=False)
            if membro:
                endereco.membro = membro
            elif request.user.is_authenticated:
                endereco.membro = Membro.objects.filter(email=request.user.email).first()
            endereco.save()
            messages.success(request, "Endereço cadastrado com sucesso!")
            return redirect('pedidos:criar_pedido')
    else:
        form = EnderecoForm()
    
    return render(request, 'enderecos/criar_endereco.html', {'form': form, 'membro': membro})

# ============= VIEWS DE PEDIDOS =============

class PedidoListView(ListView):
    model = Pedido
    template_name = 'pedidos/listar_pedidos.html'
    context_object_name = 'pedidos'
    paginate_by = 10

    def get_queryset(self):
        queryset = Pedido.objects.all().select_related('cliente', 'endereco_entrega', 'rota')
        
        # Filtros
        busca = self.request.GET.get('busca')
        if busca:
            queryset = queryset.filter(cliente__nome_completo__icontains=busca)
        
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        data_inicio = self.request.GET.get('data_inicio')
        if data_inicio:
            queryset = queryset.filter(data_entrega__date__gte=data_inicio)
        
        data_fim = self.request.GET.get('data_fim')
        if data_fim:
            queryset = queryset.filter(data_entrega__date__lte=data_fim)
        
        return queryset.order_by('-data_pedido')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = FiltroPedidoForm(self.request.GET)
        context['stats'] = {
            'pendente': Pedido.objects.filter(status='pendente').count(),
            'confirmado': Pedido.objects.filter(status='confirmado').count(),
            'em_rota': Pedido.objects.filter(status='em_rota').count(),
            'entregue': Pedido.objects.filter(status='entregue').count(),
        }
        return context

class PedidoCreateView(CreateView):
    model = Pedido
    form_class = PedidoForm
    template_name = 'pedidos/criar_pedido.html'
    success_url = reverse_lazy('pedidos:listar_pedidos')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['itens_formset'] = ItemPedidoFormSet(self.request.POST)
        else:
            context['itens_formset'] = ItemPedidoFormSet()
        
        context['produtos'] = Produto.objects.filter(disponivel=True)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        itens_formset = context['itens_formset']
        
        if itens_formset.is_valid():
            # Salvar o pedido
            self.object = form.save()
            
            # Salvar os itens
            itens_formset.instance = self.object
            itens_formset.save()
            
            # Recalcular total
            self.object.recalcular_total()
            
            messages.success(self.request, "Pedido criado com sucesso!")
            return redirect(self.get_success_url())
        else:
            return self.render_to_response(self.get_context_data(form=form))

class PedidoDetailView(DetailView):
    model = Pedido
    template_name = 'pedidos/detalhe_pedido.html'
    context_object_name = 'pedido'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['itens'] = self.object.itens.all()
        return context

class PedidoUpdateView(UpdateView):
    model = Pedido
    form_class = PedidoForm
    template_name = 'pedidos/editar_pedido.html'
    success_url = reverse_lazy('pedidos:listar_pedidos')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['itens_formset'] = ItemPedidoFormSet(self.request.POST, instance=self.object)
        else:
            context['itens_formset'] = ItemPedidoFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        itens_formset = context['itens_formset']
        
        if itens_formset.is_valid():
            self.object = form.save()
            itens_formset.instance = self.object
            itens_formset.save()
            self.object.recalcular_total()
            messages.success(self.request, "Pedido atualizado com sucesso!")
            return redirect(self.get_success_url())
        return self.render_to_response(self.get_context_data(form=form))

@login_required
def pedido_enviar_whatsapp(request, pk):
    """Envia detalhes do pedido via WhatsApp"""
    pedido = get_object_or_404(Pedido, pk=pk)
    
    # Construir mensagem
    mensagem = f"*NOVO PEDIDO ARTGELO*\n\n"
    mensagem += f"*Cliente:* {pedido.cliente.nome_completo}\n"
    mensagem += f"*Telefone:* {pedido.cliente.telefone}\n"
    mensagem += f"*Endereço:* {pedido.endereco_entrega.endereco_completo}\n" if pedido.endereco_entrega else ""
    mensagem += f"*Data Entrega:* {pedido.data_entrega.strftime('%d/%m/%Y %H:%M')}\n"
    mensagem += f"*Status:* {pedido.get_status_display()}\n\n"
    mensagem += "*Itens:*\n"
    for item in pedido.itens.all():
        mensagem += f"• {item.quantidade}kg de {item.produto.nome} - R$ {item.subtotal:.2f}\n"
    mensagem += f"\n*Total:* R$ {pedido.valor_total:.2f}\n"
    
    if pedido.observacoes:
        mensagem += f"\n*Observações:* {pedido.observacoes}"
    
    # Codificar para URL do WhatsApp
    from urllib.parse import quote
    mensagem_codificada = quote(mensagem)
    
    from django.conf import settings
    numero = settings.WHATSAPP_NUMBER
    url = f"https://wa.me/{numero}?text={mensagem_codificada}"
    
    return redirect(url)

# ============= VIEWS DE ROTAS =============

class RotaListView(ListView):
    model = Rota
    template_name = 'rotas/listar_rotas.html'
    context_object_name = 'rotas'
    paginate_by = 10

    def get_queryset(self):
        queryset = Rota.objects.all()
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        data = self.request.GET.get('data')
        if data:
            queryset = queryset.filter(data=data)
        return queryset.order_by('-data', 'nome')

class RotaCreateView(CreateView):
    model = Rota
    form_class = RotaForm
    template_name = 'rotas/criar_rota.html'
    success_url = reverse_lazy('rotas:listar_rotas')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Carregar pedidos não associados a rotas
        pedidos_disponiveis = Pedido.objects.filter(
            Q(rota__isnull=True) | Q(rota=None),
            status__in=['confirmado', 'pendente']
        ).select_related('cliente', 'endereco_entrega')
        context['pedidos_disponiveis'] = pedidos_disponiveis
        return context

    def form_valid(self, form):
        self.object = form.save()
        messages.success(self.request, "Rota criada com sucesso!")
        return redirect(self.get_success_url())

class RotaDetailView(DetailView):
    model = Rota
    template_name = 'rotas/detalhe_rota.html'
    context_object_name = 'rota'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pedidos = self.object.pedidos.all().select_related('cliente', 'endereco_entrega')
        context['pedidos'] = pedidos
        context['total_valor'] = sum(p.valor_total for p in pedidos)
        return context

@login_required
def rota_calcular_distancias(request, pk):
    """API para calcular distâncias dos pedidos na rota"""
    rota = get_object_or_404(Rota, pk=pk)
    pedidos = rota.pedidos.all().select_related('endereco_entrega')
    
    resultados = []
    # Simular cálculo de distância (usar API real em produção)
    for pedido in pedidos:
        if pedido.endereco_entrega and pedido.endereco_entrega.latitude:
            resultados.append({
                'pedido_id': pedido.pk,
                'cliente': pedido.cliente.nome_completo,
                'endereco': str(pedido.endereco_entrega),
                'latitude': pedido.endereco_entrega.latitude,
                'longitude': pedido.endereco_entrega.longitude,
                'valor': float(pedido.valor_total),
            })
    
    return JsonResponse({'pedidos': resultados, 'total': len(resultados)})

# ============= VIEWS DE AGENDAMENTO DE LIMPEZA =============

class AgendamentoListView(ListView):
    model = AgendamentoLimpeza
    template_name = 'agendamentos/listar_agendamentos.html'
    context_object_name = 'agendamentos'
    paginate_by = 20

    def get_queryset(self):
        queryset = AgendamentoLimpeza.objects.all()
        filtro = self.request.GET.get('filtro')
        if filtro == 'pendente':
            queryset = queryset.filter(confirmado=False)
        elif filtro == 'confirmado':
            queryset = queryset.filter(confirmado=True)
        return queryset.order_by('data_hora')

class AgendamentoCreateView(CreateView):
    model = AgendamentoLimpeza
    form_class = AgendamentoLimpezaForm
    template_name = 'agendamentos/criar_agendamento.html'
    success_url = reverse_lazy('agendamentos:listar_agendamentos')

    def form_valid(self, form):
        self.object = form.save()
        messages.success(self.request, "Agendamento de limpeza criado com sucesso!")
        
        # Enviar WhatsApp de confirmação
        self.enviar_whatsapp_confirmacao(self.object)
        
        return redirect(self.get_success_url())
    
    def enviar_whatsapp_confirmacao(self, agendamento):
        """Envia confirmação via WhatsApp"""
        mensagem = f"*AGENDAMENTO DE LIMPEZA ARTGELO*\n\n"
        mensagem += f"*Cliente:* {agendamento.nome_cliente}\n"
        mensagem += f"*Telefone:* {agendamento.telefone}\n"
        mensagem += f"*Data/Hora:* {agendamento.data_hora.strftime('%d/%m/%Y %H:%M')}\n"
        mensagem += f"*Tipo Freezer:* {agendamento.tipo_freezer}\n"
        mensagem += f"*Endereço:* {agendamento.endereco.endereco_completo}\n"
        if agendamento.observacoes:
            mensagem += f"*Observações:* {agendamento.observacoes}"
        
        # Aqui você pode integrar com WhatsApp ou salvar para envio posterior
        # Por enquanto, apenas loga a mensagem
        print(f"Mensagem WhatsApp: {mensagem}")

# ============= VIEWS DE DASHBOARD =============

@login_required
def dashboard(request):
    """Dashboard com estatísticas do sistema"""
    
    # Estatísticas gerais
    total_pedidos = Pedido.objects.count()
    pedidos_pendentes = Pedido.objects.filter(status='pendente').count()
    pedidos_em_rota = Pedido.objects.filter(status='em_rota').count()
    pedidos_entregues = Pedido.objects.filter(status='entregue').count()
    pedidos_hoje = Pedido.objects.filter(data_entrega__date=timezone.now().date()).count()
    
    # Valor total de pedidos
    valor_total = Pedido.objects.aggregate(Sum('valor_total'))['valor_total__sum'] or 0
    
    # Membros
    total_membros = Membro.objects.count()
    membros_ativos = Membro.objects.filter(status=True).count()
    
    # Rotas ativas
    rotas_ativas = Rota.objects.filter(status='em_andamento').count()
    
    # Agendamentos
    agendamentos_hoje = AgendamentoLimpeza.objects.filter(
        data_hora__date=timezone.now().date(),
        confirmado=True
    ).count()
    
    # Pedidos por status (para gráfico)
    pedidos_por_status = {
        'Pendente': Pedido.objects.filter(status='pendente').count(),
        'Confirmado': Pedido.objects.filter(status='confirmado').count(),
        'Em Rota': Pedido.objects.filter(status='em_rota').count(),
        'Entregue': Pedido.objects.filter(status='entregue').count(),
        'Cancelado': Pedido.objects.filter(status='cancelado').count(),
    }
    
    # Produtos mais vendidos
    produtos_mais_vendidos = ItemPedido.objects.values(
        'produto__nome'
    ).annotate(
        total_quantidade=Sum('quantidade'),
        total_valor=Sum('subtotal')
    ).order_by('-total_quantidade')[:5]
    
    context = {
        'total_pedidos': total_pedidos,
        'pedidos_pendentes': pedidos_pendentes,
        'pedidos_em_rota': pedidos_em_rota,
        'pedidos_entregues': pedidos_entregues,
        'pedidos_hoje': pedidos_hoje,
        'valor_total': valor_total,
        'total_membros': total_membros,
        'membros_ativos': membros_ativos,
        'rotas_ativas': rotas_ativas,
        'agendamentos_hoje': agendamentos_hoje,
        'pedidos_por_status': pedidos_por_status,
        'produtos_mais_vendidos': produtos_mais_vendidos,
        'ultimos_pedidos': Pedido.objects.order_by('-data_pedido')[:5],
        'proximos_agendamentos': AgendamentoLimpeza.objects.filter(
            data_hora__gte=timezone.now(),
            confirmado=True
        ).order_by('data_hora')[:5],
    }
    
    return render(request, 'dashboard.html', context)

# ============= VIEWS DE API E UTILITÁRIOS =============

@login_required
def api_enderecos_por_membro(request):
    """API para carregar endereços de um membro via AJAX"""
    membro_id = request.GET.get('membro_id')
    if not membro_id:
        return JsonResponse({'error': 'membro_id não fornecido'}, status=400)
    
    enderecos = Endereco.objects.filter(membro_id=membro_id)
    data = [{
        'id': e.id,
        'text': str(e),
        'principal': e.principal
    } for e in enderecos]
    
    return JsonResponse({'results': data})

@login_required
def api_calcular_valor_pedido(request):
    """API para calcular valor total do pedido em tempo real"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    import json
    data = json.loads(request.body)
    
    total = 0
    itens = data.get('itens', [])
    
    for item in itens:
        try:
            produto_id = item.get('produto_id')
            quantidade = float(item.get('quantidade', 0))
            
            if produto_id and quantidade > 0:
                produto = Produto.objects.get(pk=produto_id)
                subtotal = quantidade * float(produto.preco_kg)
                total += subtotal
        except (Produto.DoesNotExist, ValueError):
            pass
    
    return JsonResponse({
        'total': round(total, 2),
        'total_formatado': f'R$ {total:.2f}'
    })

# ============= VIEWS DE PÁGINAS ESTÁTICAS =============

def home(request):
    """Página inicial com efeito 3D e apresentação dos serviços"""
    return render(request, 'home.html')

def sobre(request):
    """Página sobre a empresa"""
    return render(request, 'sobre.html')

def servicos(request):
    """Página de serviços oferecidos"""
    produtos = Produto.objects.filter(disponivel=True)
    return render(request, 'servicos.html', {'produtos': produtos})
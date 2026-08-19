# urls.py
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin

from . import views

app_name = 'artgelo'

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Home
    path('', views.home, name='home'),
    path('sobre/', views.sobre, name='sobre'),
    path('servicos/', views.servicos, name='servicos'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Membros (já existentes)
    path('membros/', views.MembroListView.as_view(), name='listar_membro'),
    path('membros/criar/', views.MembroCreateView.as_view(), name='criar_membro'),
    path('membros/<int:pk>/editar/', views.MembroUpdateView.as_view(), name='editar_membro'),
    path('membros/<int:pk>/deletar/', views.MembroDeleteView.as_view(), name='deletar_membro'),
    
    # Produtos
    path('produtos/', views.ProdutoListView.as_view(), name='listar_produtos'),
    
    # Endereços
    path('enderecos/criar/', views.endereco_create, name='criar_endereco'),
    path('enderecos/criar/<int:membro_id>/', views.endereco_create, name='criar_endereco_membro'),
    
    # Pedidos
    path('pedidos/', views.PedidoListView.as_view(), name='listar_pedidos'),
    path('pedidos/criar/', views.PedidoCreateView.as_view(), name='criar_pedido'),
    path('pedidos/<int:pk>/', views.PedidoDetailView.as_view(), name='detalhe_pedido'),
    path('pedidos/<int:pk>/editar/', views.PedidoUpdateView.as_view(), name='editar_pedido'),
    path('pedidos/<int:pk>/whatsapp/', views.pedido_enviar_whatsapp, name='enviar_whatsapp'),
    
    # Rotas
    path('rotas/', views.RotaListView.as_view(), name='listar_rotas'),
    path('rotas/criar/', views.RotaCreateView.as_view(), name='criar_rota'),
    path('rotas/<int:pk>/', views.RotaDetailView.as_view(), name='detalhe_rota'),
    path('rotas/<int:pk>/calcular/', views.rota_calcular_distancias, name='calcular_rota'),
    
    # Agendamentos
    path('agendamentos/', views.AgendamentoListView.as_view(), name='listar_agendamentos'),
    path('agendamentos/criar/', views.AgendamentoCreateView.as_view(), name='criar_agendamento'),
    
    # APIs
    path('api/enderecos-por-membro/', views.api_enderecos_por_membro, name='api_enderecos_por_membro'),
    path('api/calcular-valor-pedido/', views.api_calcular_valor_pedido, name='api_calcular_valor_pedido'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
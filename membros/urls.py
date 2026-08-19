# serve para ligar uma rota da internet a uma função (view) no código
from django.urls import path

from . import views

app_name = 'membros'

urlpatterns = [
    path('', views.MembroListView.as_view(), name='listar_membro'),
    path('criar/', views.MembroCreateView.as_view(), name='criar_membro'),
    path('<int:pk>/editar/', views.MembroUpdateView.as_view(), name='editar_membro'),
    path('<int:pk>/deletar/', views.MembroDeleteView.as_view(), name='deletar_membro'),
]
# contém as funções que processam as requisições e retornam as respostas
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from .forms import MembroForm
from .models import Membro


class MembroListView(ListView):
    """Lista todos os membros, com busca por nome e filtro por status."""
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


class MembroCreateView(SuccessMessageMixin, CreateView):
    """Cria um novo membro."""
    model = Membro
    form_class = MembroForm
    template_name = 'membros/criar_membro.html'
    success_url = reverse_lazy('membros:listar_membro')
    success_message = "Membro '%(nome_completo)s' cadastrado com sucesso!"


class MembroUpdateView(SuccessMessageMixin, UpdateView):
    """Edita um membro existente."""
    model = Membro
    form_class = MembroForm
    template_name = 'membros/editar_membro.html'
    success_url = reverse_lazy('membros:listar_membro')
    success_message = "Membro '%(nome_completo)s' atualizado com sucesso!"


class MembroDeleteView(DeleteView):
    """Confirma e executa a exclusão de um membro."""
    model = Membro
    template_name = 'membros/confirmar_deleção.html'
    success_url = reverse_lazy('membros:listar_membro')

    def form_valid(self, form):
        # Guarda o nome antes de deletar, pra usar na mensagem de sucesso
        nome = self.object.nome_completo
        response = super().form_valid(form)
        messages.success(self.request, f"Membro '{nome}' removido com sucesso!")
        return response

"""
Modelos do sistema de pedidos da Artgelo.

Cole este conteúdo no models.py do app onde o modelo `Membro` já existe
(ele precisa estar importado/definido no mesmo arquivo, ou faça
`from .models import Membro` se estiver em outro app).
"""

from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse


class Produto(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField()
    preco_kg = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    imagem = models.ImageField(upload_to='produtos/', blank=True, null=True)
    disponivel = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Produto"
        verbose_name_plural = "Produtos"
        ordering = ['nome']  # noqa: RUF012

    def __str__(self):
        return f"{self.nome} (R$ {self.preco_kg}/kg)"


class Endereco(models.Model):
    membro = models.ForeignKey('Membro', on_delete=models.CASCADE, related_name='enderecos')
    rua = models.CharField(max_length=200)
    numero = models.CharField(max_length=20)
    bairro = models.CharField(max_length=100)
    cidade = models.CharField(max_length=100)
    cep = models.CharField(max_length=9)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    principal = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Endereço"
        verbose_name_plural = "Endereços"
        ordering = ['-principal', 'cidade', 'bairro']  # noqa: RUF012

    def __str__(self):
        return f"{self.rua}, {self.numero} - {self.bairro}, {self.cidade}"

    @property
    def endereco_completo(self):
        return f"{self.rua}, {self.numero} - {self.bairro}, {self.cidade} - CEP {self.cep}"

    def save(self, *args, **kwargs):
        # Garante que só exista um endereço principal por membro
        if self.principal:
            Endereco.objects.filter(membro=self.membro, principal=True).exclude(pk=self.pk).update(principal=False)
        super().save(*args, **kwargs)


class Rota(models.Model):
    STATUS_CHOICES = [  # noqa: RUF012
        ('planejada', 'Planejada'),
        ('em_andamento', 'Em Andamento'),
        ('concluida', 'Concluída'),
        ('cancelada', 'Cancelada'),
    ]

    nome = models.CharField(max_length=100)
    data = models.DateField()
    motorista = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planejada')
    pedidos = models.ManyToManyField('Pedido', blank=True, related_name='rotas_associadas')
    distancia_total = models.FloatField(default=0, help_text="Distância total em km")
    tempo_estimado = models.DurationField(blank=True, null=True)

    class Meta:
        verbose_name = "Rota"
        verbose_name_plural = "Rotas"
        ordering = ['-data']  # noqa: RUF012

    def __str__(self):
        return f"{self.nome} - {self.data.strftime('%d/%m/%Y')} ({self.get_status_display()})"

    @property
    def total_entregas(self):
        return self.pedidos.count()


class Pedido(models.Model):
    STATUS_CHOICES = [  # noqa: RUF012
        ('pendente', 'Pendente'),
        ('confirmado', 'Confirmado'),
        ('em_rota', 'Em Rota'),
        ('entregue', 'Entregue'),
        ('cancelado', 'Cancelado'),
    ]

    cliente = models.ForeignKey('Membro', on_delete=models.CASCADE, related_name='pedidos')
    endereco_entrega = models.ForeignKey(Endereco, on_delete=models.SET_NULL, null=True)
    data_pedido = models.DateTimeField(auto_now_add=True)
    data_entrega = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente')
    valor_total = models.DecimalField(max_digits=10, decimal_places=2, default=0, editable=False)
    observacoes = models.TextField(blank=True, null=True)
    rota = models.ForeignKey(Rota, on_delete=models.SET_NULL, null=True, blank=True, related_name='pedidos_diretos')

    class Meta:
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"
        # ordering = ['-data_pedido']


    def __str__(self):
        return f"Pedido #{self.pk} - {self.cliente.nome_completo} ({self.get_status_display()})"

    def get_absolute_url(self):
        return reverse('pedido_detail', kwargs={'pk': self.pk})

    def recalcular_total(self, salvar=True):
        """Soma os subtotais de todos os itens e atualiza valor_total."""
        total = self.itens.aggregate(soma=models.Sum('subtotal'))['soma'] or 0
        self.valor_total = total
        if salvar:
            self.save(update_fields=['valor_total'])
        return total


class ItemPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='itens')
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, editable=False, default=0)

    class Meta:
        verbose_name = "Item do Pedido"
        verbose_name_plural = "Itens do Pedido"

    def __str__(self):
        return f"{self.quantidade}kg de {self.produto.nome}"

    def save(self, *args, **kwargs):
        # Preenche preco_unitario automaticamente se não informado
        if not self.preco_unitario:
            self.preco_unitario = self.produto.preco_kg
        self.subtotal = self.quantidade * self.preco_unitario
        super().save(*args, **kwargs)
        # Atualiza o total do pedido pai sempre que um item muda
        self.pedido.recalcular_total()

    def delete(self, *args, **kwargs):
        pedido = self.pedido
        super().delete(*args, **kwargs)
        pedido.recalcular_total()


class AgendamentoLimpeza(models.Model):
    nome_cliente = models.CharField(max_length=200)
    telefone = models.CharField(max_length=20)
    endereco = models.ForeignKey(Endereco, on_delete=models.CASCADE)
    data_hora = models.DateTimeField()
    tipo_freezer = models.CharField(max_length=100)
    observacoes = models.TextField(blank=True, null=True)
    confirmado = models.BooleanField(default=False)
    data_criacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Agendamento de Limpeza"
        verbose_name_plural = "Agendamentos de Limpeza"
        ordering = ['data_hora']  # noqa: RUF012

    def __str__(self):
        return f"{self.nome_cliente} - {self.data_hora.strftime('%d/%m/%Y %H:%M')}"
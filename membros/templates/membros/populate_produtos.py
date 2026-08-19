# populate_produtos.py
from membros.models import Produto  # Use o nome do seu app


def run():
    produtos = [
        {
            'nome': 'Gelo em Cubo',
            'descricao': 'Gelo de alta qualidade para bebidas, eventos e uso comercial.',
            'preco_kg': 1.50,
            'disponivel': True
        },
        {
            'nome': 'Gelo em Escama',
            'descricao': 'Ideal para pesca, conservação de alimentos e aplicações industriais.',
            'preco_kg': 1.20,
            'disponivel': True
        },
        {
            'nome': 'Gelo Seco',
            'descricao': 'Gelo de dióxido de carbono para transporte de itens perecíveis.',
            'preco_kg': 4.00,
            'disponivel': True
        },
        {
            'nome': 'Gelo em Barras',
            'descricao': 'Grandes blocos de gelo para conservação e transporte.',
            'preco_kg': 0.90,
            'disponivel': True
        },
    ]
    
    for p in produtos:
        Produto.objects.get_or_create(
            nome=p['nome'],
            defaults={
                'descricao': p['descricao'],
                'preco_kg': p['preco_kg'],
                'disponivel': p['disponivel']
            }
        )
    
    print("Produtos criados com sucesso!")
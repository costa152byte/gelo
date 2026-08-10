from django.db import models


class Membro(models.Model):
    """
    Classe Membro - Define a tabela de membros no banco de dados.
    Cada atributo se torna uma coluna na tabela.
    A tabela será chamada 'membros_membro' (app_nome_modelo)
    """
    #campo para nome completo do membro
    #charfield - campo para texto com tamanho definido 

    nome_completo = models.CharField(
        max_length=200,#max 200 caracter
        verbose_name="Nome Completo"#nome que aparece nop admin
    )
    # campo para e-mail do memebro 
    #emailfield = campo espcifico para e-mails (valida formato)
    email = models.EmailField(
        unique=True,# Não permite emails duplilcados
        verbose_name="E-mail"#nome que aparece no admin
    )
    #campo para o telefone do membro 
    # charfielld = campo de texto
    verbose_name = "Telefone"
    telefone = models.CharField(
        max_length=20, #max 20 caracter
        blank=True,#pode ficar vazio no formulario 
        null=True,# pode ser null no banco de dados (ou seja pode ficar vazio )
        verbose_name="Telefone"
    )
 
    data_cadastro = models.DateField(
        auto_now_add=True,
        verbose_name="Data de Cadastro"
    )
    
 
    status = models.BooleanField(
        default=True,
        verbose_name="Ativo"
    )
    
 
    TIPO_CHOICES = [  # noqa: RUF012
        ('voluntario', 'Voluntário'),
        ('doador', 'Doador'),
        ('parceiro', 'Parceiro'),
    ]
    tipo_membro = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        default='voluntario',
        verbose_name="Tipo de Membro"
    )
    
 
    def __str__(self):
        """
        Método que define como o objeto será exibido como texto.
        Quando o Django mostrar este modelo (no Admin, em listas),
        aparecerá o nome completo do membro.
        """
        return self.nome_completo
 
    class Meta:
        """
        Classe Meta - Configurações adicionais do modelo
        """
        verbose_name = "Membro"
 
        verbose_name_plural = "Membros"
  
        ordering = ['nome_completo']  # noqa: RUF012

# Create your models here.
# banco de dados
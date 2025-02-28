from django.db import models


class Vendedor(models.Model):
    cpf = models.CharField(max_length=11, unique=True, null=True)
    nome = models.CharField(max_length=255)
    data_cadastro = models.DateTimeField(auto_now_add=True)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return self.nome

    @property
    def comissao_total(self):
        # Soma todas as comissões das vendas do vendedor
        total_comissao = self.vendas.aggregate(models.Sum("valor_comissao"))[
            "valor_comissao__sum"
        ]
        return (
            total_comissao if total_comissao is not None else 0
        )  # Retorna 0 se não houver vendas

    @property
    def total_vendas(self):
        # Soma o valor total de todas as vendas do vendedor
        total_vendas = self.vendas.aggregate(models.Sum("valor_total"))[
            "valor_total__sum"
        ]
        return (
            total_vendas if total_vendas is not None else 0
        )  # Retorna 0 se não houver vendas

    @property
    def ultima_venda(self):
        # Obtém a data da última venda do vendedor
        ultima = self.vendas.order_by("-data_venda").first()
        return ultima.data_venda if ultima else None

    @property
    def ultima_venda_valor(self):
        # Obtém o valor da última venda do vendedor
        ultima = self.vendas.order_by("-data_venda").first()
        return ultima.valor_total if ultima else None

    @property
    def ultima_venda_comissao(self):
        # Obtém o valor da última venda do vendedor
        ultima = self.vendas.order_by("-data_venda").first()
        return ultima.valor_comissao if ultima else None
    
    @property
    def vendas(self):
        return self.vendas
    

    class Meta:
        verbose_name = "Vendedor"
        verbose_name_plural = "Vendedores"


"""

from django.db import models
from decimal import Decimal


class Vendedor(models.Model):
    nome = models.CharField(max_length=255)
    data_cadastro = models.DateTimeField(auto_now_add=True)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return self.nome

    @property
    def comissao_total(self):
        # Soma todas as comissões das vendas do vendedor
        total_comissao = self.vendas.aggregate(models.Sum("valor_comissao"))["valor_comissao__sum"]
        # Retorna 0 se não houver vendas
        return Decimal(total_comissao if total_comissao is not None else 0)

    @property
    def total_vendas(self):
        # Soma o valor total de todas as vendas do vendedor
        total_vendas = self.vendas.aggregate(models.Sum("valor_total"))["valor_total__sum"]
        # Retorna 0 se não houver vendas
        return Decimal(total_vendas if total_vendas is not None else 0)

    @property
    def ultima_venda(self):
        # Obtém a data da última venda do vendedor
        try:
            ultima = self.vendas.latest('data_venda')  # Obtém a última venda mais eficientemente
            return ultima.data_venda
        except Venda.DoesNotExist:
            return None


"""

from django.db import models
from apps.vendedores.models import Vendedor
from django.db.models import Sum


class RelatorioComissao(models.Model):
    vendedor = models.ForeignKey(
        Vendedor, on_delete=models.CASCADE, related_name="relatorios"
    )
    periodo_inicio = models.DateField()
    periodo_fim = models.DateField()
    total_vendas = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_comissao = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def calcular_totais(self):
        """Calcula o total de vendas e comissão no período."""
        vendas_periodo = self.vendedor.vendas.filter(
            data_venda__range=(self.periodo_inicio, self.periodo_fim)
        )
        # Calcula o total de vendas
        self.total_vendas = (
            vendas_periodo.aggregate(Sum("valor_total"))["valor_total__sum"] or 0
        )
        # Calcula o total de comissão
        self.total_comissao = (
            vendas_periodo.aggregate(Sum("valor_comissao"))["valor_comissao__sum"] or 0
        )

    def save(self, *args, **kwargs):
        self.calcular_totais()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Relatório {self.vendedor.nome} - {self.periodo_inicio.strftime('%d/%m/%Y')} a {self.periodo_fim.strftime('%d/%m/%Y')}"

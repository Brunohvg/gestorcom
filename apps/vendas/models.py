from decimal import Decimal, ROUND_HALF_UP
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from apps.vendedores.models import Vendedor
from apps.dashboard.models import RelatorioComissao
import calendar

COMISSAO_PERCENTUAL = Decimal("0.01")  # 1% fixo


class Venda(models.Model):
    vendedor = models.ForeignKey(
        Vendedor, related_name="vendas", on_delete=models.CASCADE
    )
    valor_total = models.DecimalField(max_digits=10, decimal_places=2)
    valor_comissao = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )
    data_venda = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Venda #{self.id} - Vendedor: {self.vendedor.nome}"

    def clean(self):
        # Verifica se o valor_total é maior que zero
        if self.valor_total is None or self.valor_total <= 0:
            raise ValidationError("O valor total da venda deve ser maior que zero.")

        # Verifica se o valor da comissão é negativo
        if self.valor_comissao is not None and self.valor_comissao < 0:
            raise ValidationError("O valor da comissão não pode ser negativo.")

    def calcular_comissao(self):
        """Calcula a comissão fixa de 1% sobre o valor total da venda."""
        return (Decimal(self.valor_total) * COMISSAO_PERCENTUAL).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

    def save(self, *args, **kwargs):
        if self.valor_comissao is None:  # Calcula comissão apenas se não existir
            self.valor_comissao = self.calcular_comissao()

        super().save(*args, **kwargs)

        # Após salvar a venda, verificamos se o relatório já existe para o período
        periodo_inicio = self.data_venda.replace(day=1)  # Assume o primeiro dia do mês
        # Calculando o último dia do mês
        ultimo_dia = calendar.monthrange(self.data_venda.year, self.data_venda.month)[1]
        periodo_fim = self.data_venda.replace(day=ultimo_dia)  # Último dia do mês

        relatorio, created = RelatorioComissao.objects.get_or_create(
            vendedor=self.vendedor,
            periodo_inicio=periodo_inicio,
            periodo_fim=periodo_fim,
        )

        # Atualiza o relatório
        relatorio.calcular_totais()  # Atualiza os totais de vendas e comissão
        relatorio.save()

    class Meta:
        verbose_name = "Venda"
        verbose_name_plural = "Vendas"
        ordering = ["-data_venda"]

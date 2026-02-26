from decimal import Decimal, ROUND_HALF_UP

from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError

from apps.vendedores.models import Vendedor
from apps.dashboard.models import RelatorioComissao
import calendar


class Venda(models.Model):
    vendedor = models.ForeignKey(
        Vendedor, related_name="vendas", on_delete=models.CASCADE
    )
    valor_total = models.DecimalField(max_digits=10, decimal_places=2)
    valor_comissao = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )
    taxa_aplicada = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Taxa (%) aplicada no momento do registro. Imutável após criação.",
    )
    data_venda = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Venda #{self.id} - Vendedor: {self.vendedor.nome}"

    def clean(self):
        if self.valor_total is None or self.valor_total <= 0:
            raise ValidationError("O valor total da venda deve ser maior que zero.")

        if self.valor_comissao is not None and self.valor_comissao < 0:
            raise ValidationError("O valor da comissão não pode ser negativo.")

    def calcular_comissao(self):
        """Calcula comissão usando taxa configurável (snapshot)."""
        from apps.comissoes.services import obter_taxa, calcular_comissao

        if self.taxa_aplicada is None:
            self.taxa_aplicada = obter_taxa(self.vendedor, self.valor_total)

        return calcular_comissao(self.valor_total, self.taxa_aplicada).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

    def save(self, *args, **kwargs):
        if self.valor_comissao is None:
            self.valor_comissao = self.calcular_comissao()

        super().save(*args, **kwargs)

        # Atualiza relatório do período
        from datetime import date as date_type
        dt = self.data_venda
        if hasattr(dt, 'date'):
            dt = dt.date()
        elif isinstance(dt, str):
            from datetime import date
            dt = date.fromisoformat(dt[:10])
        periodo_inicio = dt.replace(day=1)
        ultimo_dia = calendar.monthrange(dt.year, dt.month)[1]
        periodo_fim = dt.replace(day=ultimo_dia)

        relatorio, _ = RelatorioComissao.objects.get_or_create(
            vendedor=self.vendedor,
            periodo_inicio=periodo_inicio,
            periodo_fim=periodo_fim,
        )
        relatorio.calcular_totais()
        relatorio.save()

    class Meta:
        verbose_name = "Venda"
        verbose_name_plural = "Vendas"
        ordering = ["-data_venda"]

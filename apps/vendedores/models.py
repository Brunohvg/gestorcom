from django.db import models
from django.core.validators import RegexValidator


class Vendedor(models.Model):
    cpf = models.CharField(
        max_length=11,
        unique=True,
        validators=[
            RegexValidator(
                regex=r"^\d{11}$",
                message="O CPF deve conter exatamente 11 dígitos numéricos.",
            )
        ],
    )
    nome = models.CharField(max_length=255)
    data_cadastro = models.DateTimeField(auto_now_add=True)
    ativo = models.BooleanField(default=True)
    taxa_comissao = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Taxa individual (%). Se vazio, usa taxa padrão ou faixas.",
    )

    def __str__(self):
        return self.nome

    @property
    def comissao_total(self):
        from decimal import Decimal

        total = self.vendas.aggregate(models.Sum("valor_comissao"))[
            "valor_comissao__sum"
        ]
        return Decimal(total) if total is not None else Decimal("0.00")

    @property
    def total_vendas(self):
        from decimal import Decimal

        total = self.vendas.aggregate(models.Sum("valor_total"))["valor_total__sum"]
        return Decimal(total) if total is not None else Decimal("0.00")

    @property
    def ultima_venda(self):
        ultima = self.vendas.order_by("-data_venda").first()
        return ultima.data_venda if ultima else None

    @property
    def ultima_venda_valor(self):
        ultima = self.vendas.order_by("-data_venda").first()
        return ultima.valor_total if ultima else None

    @property
    def ultima_venda_comissao(self):
        ultima = self.vendas.order_by("-data_venda").first()
        return ultima.valor_comissao if ultima else None

    class Meta:
        verbose_name = "Vendedor"
        verbose_name_plural = "Vendedores"

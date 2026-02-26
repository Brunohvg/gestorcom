from decimal import Decimal

from django.conf import settings
from django.db import models

from apps.vendedores.models import Vendedor


# ---------------------------------------------------------------------------
# Configuração Global
# ---------------------------------------------------------------------------

class ConfiguracaoComissao(models.Model):
    """Singleton com a taxa padrão de comissão do sistema."""

    taxa_padrao = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("1.00"),
        help_text="Taxa padrão de comissão (%) quando não há configuração específica.",
    )
    atualizado_em = models.DateTimeField(auto_now=True)
    atualizado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    class Meta:
        verbose_name = "Configuração de Comissão"
        verbose_name_plural = "Configuração de Comissão"

    def __str__(self):
        return f"Taxa padrão: {self.taxa_padrao}%"

    def save(self, *args, **kwargs):
        self.pk = 1  # Singleton
        super().save(*args, **kwargs)

    @classmethod
    def get(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


# ---------------------------------------------------------------------------
# Faixas Escalonadas
# ---------------------------------------------------------------------------

class FaixaComissao(models.Model):
    """Faixa escalonada de comissão. Se vendedor=null, é faixa global."""

    vendedor = models.ForeignKey(
        Vendedor,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="faixas_comissao",
        help_text="Vazio = faixa global aplicável a todos.",
    )
    valor_minimo = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Valor mínimo de vendas no mês (inclusive).",
    )
    valor_maximo = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Valor máximo (inclusive). Vazio = sem limite.",
    )
    taxa = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Taxa de comissão (%) para esta faixa.",
    )

    class Meta:
        verbose_name = "Faixa de Comissão"
        verbose_name_plural = "Faixas de Comissão"
        ordering = ["vendedor", "valor_minimo"]

    def __str__(self):
        vendedor_label = self.vendedor.nome if self.vendedor else "GLOBAL"
        maximo = f"R$ {self.valor_maximo}" if self.valor_maximo else "∞"
        return f"{vendedor_label}: R$ {self.valor_minimo} – {maximo} → {self.taxa}%"

    def contem_valor(self, valor):
        """Verifica se o valor está dentro desta faixa."""
        if valor < self.valor_minimo:
            return False
        if self.valor_maximo is not None and valor > self.valor_maximo:
            return False
        return True


# ---------------------------------------------------------------------------
# Histórico de Alterações
# ---------------------------------------------------------------------------

class HistoricoTaxaComissao(models.Model):
    """Log auditável de alterações de taxa de comissão."""

    vendedor = models.ForeignKey(
        Vendedor,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="historico_taxas",
        help_text="Vazio = alteração na taxa global.",
    )
    taxa_anterior = models.DecimalField(max_digits=5, decimal_places=2)
    taxa_nova = models.DecimalField(max_digits=5, decimal_places=2)
    alterado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
    )
    alterado_em = models.DateTimeField(auto_now_add=True)
    motivo = models.CharField(max_length=500, blank=True, default="")

    class Meta:
        verbose_name = "Histórico de Taxa"
        verbose_name_plural = "Histórico de Taxas"
        ordering = ["-alterado_em"]

    def __str__(self):
        alvo = self.vendedor.nome if self.vendedor else "GLOBAL"
        return f"{alvo}: {self.taxa_anterior}% → {self.taxa_nova}% em {self.alterado_em:%d/%m/%Y}"


# ---------------------------------------------------------------------------
# Competência (Ciclo Mensal)
# ---------------------------------------------------------------------------

class Competencia(models.Model):
    """Representa um ciclo mensal de comissões."""

    class Status(models.TextChoices):
        ABERTA = "ABERTA", "Aberta"
        EM_CONFERENCIA = "EM_CONFERENCIA", "Em Conferência"
        ENVIADA = "ENVIADA", "Enviada para Contabilidade"
        APROVADA = "APROVADA", "Aprovada para Pagamento"
        PAGA = "PAGA", "Paga"

    ano = models.PositiveIntegerField()
    mes = models.PositiveIntegerField()
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ABERTA,
    )

    enviada_em = models.DateTimeField(null=True, blank=True)
    enviada_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="competencias_enviadas",
    )
    aprovada_em = models.DateTimeField(null=True, blank=True)
    aprovada_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="competencias_aprovadas",
    )
    paga_em = models.DateTimeField(null=True, blank=True)
    paga_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="competencias_pagas",
    )

    criada_em = models.DateTimeField(auto_now_add=True)
    atualizada_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Competência"
        verbose_name_plural = "Competências"
        unique_together = ["ano", "mes"]
        ordering = ["-ano", "-mes"]

    def __str__(self):
        return f"{self.mes:02d}/{self.ano} — {self.get_status_display()}"


class ComissaoVendedor(models.Model):
    """Consolidação de comissão de um vendedor em uma competência."""

    vendedor = models.ForeignKey(
        Vendedor,
        on_delete=models.CASCADE,
        related_name="comissoes",
    )
    competencia = models.ForeignKey(
        Competencia,
        on_delete=models.CASCADE,
        related_name="comissoes_vendedores",
    )
    total_vendas = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("0.00")
    )
    total_comissao = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("0.00")
    )
    ajustes = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("0.00")
    )
    comissao_final = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("0.00")
    )

    class Meta:
        verbose_name = "Comissão por Vendedor"
        verbose_name_plural = "Comissões por Vendedor"
        unique_together = ["vendedor", "competencia"]
        ordering = ["vendedor__nome"]

    def __str__(self):
        return f"{self.vendedor.nome} — {self.competencia}"

    def calcular(self):
        """Recalcula totais a partir das vendas do período."""
        from apps.vendas.models import Venda

        vendas = Venda.objects.filter(
            vendedor=self.vendedor,
            data_venda__year=self.competencia.ano,
            data_venda__month=self.competencia.mes,
        )
        totais = vendas.aggregate(
            total_v=models.Sum("valor_total"),
            total_c=models.Sum("valor_comissao"),
        )
        self.total_vendas = totais["total_v"] or Decimal("0.00")
        self.total_comissao = totais["total_c"] or Decimal("0.00")
        self.comissao_final = self.total_comissao + self.ajustes
        self.save()

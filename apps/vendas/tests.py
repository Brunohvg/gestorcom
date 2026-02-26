from decimal import Decimal

from django.test import TestCase

from apps.vendedores.models import Vendedor
from apps.comissoes.models import ConfiguracaoComissao, FaixaComissao
from .models import Venda


class VendaModelTest(TestCase):
    """Testes do modelo Venda com comissão configurável."""

    def setUp(self):
        self.vendedor = Vendedor.objects.create(cpf="12345678901", nome="João Silva")

    def test_comissao_usa_taxa_padrao(self):
        """Sem configuração, usa taxa padrão global (1%)."""
        venda = Venda.objects.create(
            vendedor=self.vendedor,
            valor_total=Decimal("1000.00"),
            data_venda="2026-02-26",
        )
        self.assertEqual(venda.taxa_aplicada, Decimal("1.00"))
        self.assertEqual(venda.valor_comissao, Decimal("10.00"))

    def test_comissao_usa_taxa_vendedor(self):
        """Vendedor com taxa individual usa ela."""
        self.vendedor.taxa_comissao = Decimal("5.00")
        self.vendedor.save()
        venda = Venda.objects.create(
            vendedor=self.vendedor,
            valor_total=Decimal("1000.00"),
            data_venda="2026-02-26",
        )
        self.assertEqual(venda.taxa_aplicada, Decimal("5.00"))
        self.assertEqual(venda.valor_comissao, Decimal("50.00"))

    def test_comissao_usa_faixa_escalonada(self):
        """Com faixas, usa a correta para o valor."""
        FaixaComissao.objects.create(
            vendedor=self.vendedor,
            valor_minimo=Decimal("0"),
            valor_maximo=Decimal("5000"),
            taxa=Decimal("3.00"),
        )
        FaixaComissao.objects.create(
            vendedor=self.vendedor,
            valor_minimo=Decimal("5000.01"),
            valor_maximo=None,
            taxa=Decimal("7.00"),
        )
        venda_baixa = Venda.objects.create(
            vendedor=self.vendedor,
            valor_total=Decimal("3000.00"),
            data_venda="2026-02-26",
        )
        venda_alta = Venda.objects.create(
            vendedor=self.vendedor,
            valor_total=Decimal("8000.00"),
            data_venda="2026-02-26",
        )
        self.assertEqual(venda_baixa.taxa_aplicada, Decimal("3.00"))
        self.assertEqual(venda_baixa.valor_comissao, Decimal("90.00"))
        self.assertEqual(venda_alta.taxa_aplicada, Decimal("7.00"))
        self.assertEqual(venda_alta.valor_comissao, Decimal("560.00"))


class VendaValidationTest(TestCase):
    """Testes de validação de vendas via form."""

    def setUp(self):
        self.vendedor = Vendedor.objects.create(cpf="12345678901", nome="João Silva")

    def test_venda_com_valor_zero_falha(self):
        from apps.vendas.forms import VendaForm
        form = VendaForm(
            data={
                "vendedor": self.vendedor.pk,
                "valor_total": "R$ 0,00",
                "data_venda": "2026-02-26",
            }
        )
        self.assertFalse(form.is_valid())

    def test_venda_com_valor_negativo_falha(self):
        from apps.vendas.forms import VendaForm
        form = VendaForm(
            data={
                "vendedor": self.vendedor.pk,
                "valor_total": "-100",
                "data_venda": "2026-02-26",
            }
        )
        self.assertFalse(form.is_valid())


class VendaFormParsingTest(TestCase):
    """Testes de parsing de moeda BR."""

    def setUp(self):
        self.vendedor = Vendedor.objects.create(cpf="12345678901", nome="João Silva")

    def test_parse_formato_brasileiro(self):
        from apps.vendas.forms import VendaForm
        form = VendaForm(
            data={
                "vendedor": self.vendedor.pk,
                "valor_total": "R$ 1.234,56",
                "data_venda": "2026-02-26",
            }
        )
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["valor_total"], Decimal("1234.56"))

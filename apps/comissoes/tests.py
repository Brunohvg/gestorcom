from decimal import Decimal

from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from .models import (
    Competencia,
    ComissaoVendedor,
    ConfiguracaoComissao,
    FaixaComissao,
    HistoricoTaxaComissao,
)
from .services import obter_taxa, calcular_comissao, transicionar_status, registrar_alteracao_taxa
from apps.vendedores.models import Vendedor


# ---------------------------------------------------------------------------
# Testes de obter_taxa (4 camadas)
# ---------------------------------------------------------------------------

class ObterTaxaTest(TestCase):
    """Testes da resolução de taxa em 4 camadas."""

    def setUp(self):
        self.vendedor = Vendedor.objects.create(cpf="12345678901", nome="João")

    def test_fallback_taxa_padrao(self):
        """Sem nenhuma configuração, retorna taxa padrão global (1%)."""
        taxa = obter_taxa(self.vendedor, Decimal("5000"))
        self.assertEqual(taxa, Decimal("1.00"))

    def test_taxa_padrao_configurada(self):
        """Usa taxa customizada do ConfiguracaoComissao."""
        config = ConfiguracaoComissao.get()
        config.taxa_padrao = Decimal("3.00")
        config.save()
        taxa = obter_taxa(self.vendedor, Decimal("5000"))
        self.assertEqual(taxa, Decimal("3.00"))

    def test_taxa_fixa_vendedor(self):
        """Taxa fixa do vendedor prevalece sobre global."""
        self.vendedor.taxa_comissao = Decimal("5.00")
        self.vendedor.save()
        taxa = obter_taxa(self.vendedor, Decimal("5000"))
        self.assertEqual(taxa, Decimal("5.00"))

    def test_faixa_global(self):
        """Faixa global prevalece sobre taxa padrão."""
        FaixaComissao.objects.create(
            vendedor=None,
            valor_minimo=Decimal("0"),
            valor_maximo=Decimal("10000"),
            taxa=Decimal("4.00"),
        )
        taxa = obter_taxa(self.vendedor, Decimal("5000"))
        self.assertEqual(taxa, Decimal("4.00"))

    def test_faixa_vendedor_prevalece(self):
        """Faixa do vendedor prevalece sobre tudo."""
        self.vendedor.taxa_comissao = Decimal("5.00")
        self.vendedor.save()
        FaixaComissao.objects.create(
            vendedor=self.vendedor,
            valor_minimo=Decimal("0"),
            valor_maximo=Decimal("10000"),
            taxa=Decimal("7.00"),
        )
        taxa = obter_taxa(self.vendedor, Decimal("5000"))
        self.assertEqual(taxa, Decimal("7.00"))

    def test_faixa_escalonada_alta(self):
        """Valor acima de 10k usa a faixa superior."""
        FaixaComissao.objects.create(
            vendedor=self.vendedor,
            valor_minimo=Decimal("0"),
            valor_maximo=Decimal("10000"),
            taxa=Decimal("5.00"),
        )
        FaixaComissao.objects.create(
            vendedor=self.vendedor,
            valor_minimo=Decimal("10000.01"),
            valor_maximo=None,
            taxa=Decimal("8.00"),
        )
        taxa_baixa = obter_taxa(self.vendedor, Decimal("5000"))
        taxa_alta = obter_taxa(self.vendedor, Decimal("15000"))
        self.assertEqual(taxa_baixa, Decimal("5.00"))
        self.assertEqual(taxa_alta, Decimal("8.00"))


class CalcularComissaoTest(TestCase):
    """Testes do cálculo de comissão."""

    def test_calculo_simples(self):
        resultado = calcular_comissao(Decimal("1000"), Decimal("5.00"))
        self.assertEqual(resultado, Decimal("50.00"))

    def test_calculo_com_decimal(self):
        resultado = calcular_comissao(Decimal("1234.56"), Decimal("3.50"))
        self.assertEqual(resultado, Decimal("43.2096"))


# ---------------------------------------------------------------------------
# Testes de Histórico
# ---------------------------------------------------------------------------

class HistoricoTaxaTest(TestCase):
    """Testes do registro de alteração de taxa."""

    def setUp(self):
        self.vendedor = Vendedor.objects.create(cpf="12345678901", nome="João")
        self.user = User.objects.create_user(username="gestor", password="test1234")

    def test_registra_alteracao(self):
        log = registrar_alteracao_taxa(
            vendedor=self.vendedor,
            taxa_anterior=Decimal("1.00"),
            taxa_nova=Decimal("5.00"),
            usuario=self.user,
            motivo="Promoção de vendas",
        )
        self.assertEqual(log.taxa_anterior, Decimal("1.00"))
        self.assertEqual(log.taxa_nova, Decimal("5.00"))
        self.assertEqual(log.alterado_por, self.user)
        self.assertEqual(log.motivo, "Promoção de vendas")

    def test_historico_global(self):
        """Vendedor=None registra alteração na taxa global."""
        log = registrar_alteracao_taxa(
            vendedor=None,
            taxa_anterior=Decimal("1.00"),
            taxa_nova=Decimal("2.00"),
            usuario=self.user,
        )
        self.assertIsNone(log.vendedor)


# ---------------------------------------------------------------------------
# Testes de Snapshot na Venda
# ---------------------------------------------------------------------------

class VendaTaxaSnapshotTest(TestCase):
    """Testes de que a taxa é gravada na Venda como snapshot."""

    def setUp(self):
        self.vendedor = Vendedor.objects.create(
            cpf="12345678901", nome="João", taxa_comissao=Decimal("5.00")
        )

    def test_snapshot_taxa_na_criacao(self):
        from apps.vendas.models import Venda
        venda = Venda.objects.create(
            vendedor=self.vendedor,
            valor_total=Decimal("1000.00"),
            data_venda="2026-02-26",
        )
        self.assertEqual(venda.taxa_aplicada, Decimal("5.00"))
        self.assertEqual(venda.valor_comissao, Decimal("50.00"))

    def test_taxa_nao_muda_apos_alteracao_vendedor(self):
        """Mesmo que a taxa do vendedor mude, a venda já criada mantém o snapshot."""
        from apps.vendas.models import Venda
        venda = Venda.objects.create(
            vendedor=self.vendedor,
            valor_total=Decimal("1000.00"),
            data_venda="2026-02-26",
        )
        self.vendedor.taxa_comissao = Decimal("10.00")
        self.vendedor.save()
        venda.refresh_from_db()
        self.assertEqual(venda.taxa_aplicada, Decimal("5.00"))
        self.assertEqual(venda.valor_comissao, Decimal("50.00"))


# ---------------------------------------------------------------------------
# Testes de Transição de Status
# ---------------------------------------------------------------------------

class CompetenciaStatusTest(TestCase):
    """Testes de transição de status da competência."""

    def setUp(self):
        self.user = User.objects.create_user(username="gestor", password="test1234")
        self.competencia = Competencia.objects.create(ano=2026, mes=2)

    def test_aberta_para_em_conferencia(self):
        resultado = transicionar_status(
            self.competencia, Competencia.Status.EM_CONFERENCIA, self.user
        )
        self.assertEqual(resultado.status, Competencia.Status.EM_CONFERENCIA)

    def test_fluxo_completo(self):
        """Fluxo ABERTA → EM_CONFERENCIA → ENVIADA → APROVADA → PAGA."""
        transicionar_status(self.competencia, Competencia.Status.EM_CONFERENCIA, self.user)
        transicionar_status(self.competencia, Competencia.Status.ENVIADA, self.user)
        self.assertIsNotNone(self.competencia.enviada_em)
        transicionar_status(self.competencia, Competencia.Status.APROVADA, self.user)
        self.assertIsNotNone(self.competencia.aprovada_em)
        transicionar_status(self.competencia, Competencia.Status.PAGA, self.user)
        self.assertEqual(self.competencia.status, Competencia.Status.PAGA)
        self.assertIsNotNone(self.competencia.paga_em)


class CompetenciaStatusInvalidoTest(TestCase):
    """Testes de transições inválidas."""

    def setUp(self):
        self.user = User.objects.create_user(username="gestor", password="test1234")
        self.competencia = Competencia.objects.create(ano=2026, mes=2)

    def test_aberta_para_paga_rejeita(self):
        with self.assertRaises(ValidationError):
            transicionar_status(self.competencia, Competencia.Status.PAGA, self.user)

    def test_paga_para_aberta_rejeita(self):
        self.competencia.status = Competencia.Status.PAGA
        self.competencia.save()
        with self.assertRaises(ValidationError):
            transicionar_status(self.competencia, Competencia.Status.ABERTA, self.user)


class ComissaoVendedorTest(TestCase):
    """Testes de consolidação."""

    def setUp(self):
        self.vendedor = Vendedor.objects.create(cpf="12345678901", nome="João")
        self.competencia = Competencia.objects.create(ano=2026, mes=2)

    def test_unique_together(self):
        ComissaoVendedor.objects.create(vendedor=self.vendedor, competencia=self.competencia)
        with self.assertRaises(Exception):
            ComissaoVendedor.objects.create(vendedor=self.vendedor, competencia=self.competencia)

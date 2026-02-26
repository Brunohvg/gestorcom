from django.test import TestCase
from django.db import IntegrityError

from .models import Vendedor
from .forms import VendedorForm


class VendedorModelTest(TestCase):
    """Testes do modelo Vendedor."""

    def test_criar_vendedor_valido(self):
        """Cria vendedor com CPF válido de 11 dígitos."""
        vendedor = Vendedor.objects.create(cpf="12345678901", nome="Maria Souza")
        self.assertEqual(vendedor.cpf, "12345678901")
        self.assertTrue(vendedor.ativo)

    def test_cpf_duplicado_rejeita(self):
        """Dois vendedores com mesmo CPF devem ser rejeitados."""
        Vendedor.objects.create(cpf="12345678901", nome="Vendedor 1")
        with self.assertRaises(IntegrityError):
            Vendedor.objects.create(cpf="12345678901", nome="Vendedor 2")


class VendedorFormTest(TestCase):
    """Testes do formulário de vendedor."""

    def test_cpf_invalido_curto(self):
        """CPF com menos de 11 dígitos é rejeitado."""
        form = VendedorForm(data={"nome": "Teste", "cpf": "123", "ativo": True})
        self.assertFalse(form.is_valid())
        self.assertIn("cpf", form.errors)

    def test_cpf_com_letras(self):
        """CPF com letras é rejeitado."""
        form = VendedorForm(data={"nome": "Teste", "cpf": "1234567890a", "ativo": True})
        self.assertFalse(form.is_valid())

    def test_cpf_duplicado_via_form(self):
        """Form rejeita CPF já cadastrado."""
        Vendedor.objects.create(cpf="12345678901", nome="Existente")
        form = VendedorForm(data={"nome": "Novo", "cpf": "12345678901", "ativo": True})
        self.assertFalse(form.is_valid())
        self.assertIn("cpf", form.errors)

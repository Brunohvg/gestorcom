import re
from decimal import Decimal, InvalidOperation

from django import forms
from django.core.exceptions import ValidationError

from apps.vendedores.models import Vendedor


def parse_valor_br(valor_str):
    """Converte string de moeda BR (R$ 1.234,56) para Decimal."""
    if not valor_str:
        raise ValidationError("Valor é obrigatório.")
    cleaned = re.sub(r"[^\d,.\-]", "", valor_str)
    cleaned = cleaned.replace(".", "").replace(",", ".")
    try:
        return Decimal(cleaned)
    except InvalidOperation:
        raise ValidationError("Valor inválido.")


class VendaForm(forms.Form):
    vendedor = forms.ModelChoiceField(
        queryset=Vendedor.objects.all(),
        error_messages={"required": "Selecione um vendedor."},
    )
    valor_total = forms.CharField(
        error_messages={"required": "Informe o valor da venda."},
    )
    data_venda = forms.DateField(
        error_messages={"required": "Informe a data da venda."},
    )

    def clean_valor_total(self):
        valor = parse_valor_br(self.cleaned_data["valor_total"])
        if valor <= 0:
            raise ValidationError("O valor deve ser maior que zero.")
        return valor


class EditarVendaForm(forms.Form):
    valor_venda = forms.CharField(
        error_messages={"required": "Informe o novo valor."},
    )

    def clean_valor_venda(self):
        valor = parse_valor_br(self.cleaned_data["valor_venda"])
        if valor <= 0:
            raise ValidationError("O valor deve ser maior que zero.")
        return valor

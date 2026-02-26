from django import forms
from django.core.exceptions import ValidationError

from .models import Vendedor


class VendedorForm(forms.ModelForm):
    class Meta:
        model = Vendedor
        fields = ["nome", "cpf", "ativo"]

    def clean_cpf(self):
        cpf = self.cleaned_data.get("cpf", "").strip()
        if not cpf.isdigit() or len(cpf) != 11:
            raise ValidationError(
                "O CPF deve conter exatamente 11 dígitos numéricos."
            )
        qs = Vendedor.objects.filter(cpf=cpf)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError("Já existe um vendedor com este CPF.")
        return cpf

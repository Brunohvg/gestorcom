from django.shortcuts import render
from .models import RelatorioComissao
from apps.vendedores.models import Vendedor
from django.db.models import Sum


def dashboard(request):
    relatorios = RelatorioComissao.objects.all()

    top_vendedores = Vendedor.objects.annotate(
        total_vendas_calc=Sum(
            "vendas__valor_total"
        )  # Alterado o nome para evitar conflito
    ).order_by("-total_vendas_calc")[:3]

    context = {
        "relatorios": relatorios,
        "top_vendedores": top_vendedores,
    }

    return render(request, "dashboard/base.html", context)

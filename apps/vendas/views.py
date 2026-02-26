from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Venda
from .forms import VendaForm, EditarVendaForm
from apps.vendedores.models import Vendedor
from core.decorators import grupo_caixa_required


def _buscar_vendas():
    """Retorna o contexto com todas as vendas e vendedores."""
    from django.utils.timezone import now

    hoje = now().date()
    return {
        "vendedores": Vendedor.objects.filter(ativo=True),
        "vendas": Venda.objects.filter(data_venda__date=hoje),
    }


@login_required
@grupo_caixa_required
def vendas(request):
    """Lista vendas do dia e registra novas vendas."""
    if request.method == "POST":
        form = VendaForm(request.POST)
        if form.is_valid():
            Venda.objects.create(
                vendedor=form.cleaned_data["vendedor"],
                valor_total=form.cleaned_data["valor_total"],
                data_venda=form.cleaned_data["data_venda"],
            )
            messages.success(request, "Venda registrada com sucesso!")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error, extra_tags="danger")

    return render(request, "vendas/base.html", _buscar_vendas())


@login_required
@grupo_caixa_required
def editar_venda(request, venda_id):
    """Edita uma venda existente usando Decimal."""
    venda = get_object_or_404(Venda, id=venda_id)

    if request.method == "POST":
        form = EditarVendaForm(request.POST)
        if not form.is_valid():
            return JsonResponse({"message": "Erro ao processar os valores!"}, status=400)

        venda.valor_total = form.cleaned_data["valor_venda"]
        venda.valor_comissao = venda.calcular_comissao()
        venda.save()
        return redirect("vendedores:edit_vendedor", venda.vendedor.id)

    return render(request, "vendas/base.html", {"venda": venda, "vendedor": venda.vendedor})


@login_required
@grupo_caixa_required
def excluir_venda(request, venda_id):
    """Exclui uma venda com segurança."""
    get_object_or_404(Venda, id=venda_id).delete()
    messages.success(request, "Venda excluída com sucesso!")
    return redirect("vendas:vendas")

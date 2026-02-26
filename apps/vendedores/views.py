from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from .models import Vendedor
from .forms import VendedorForm
from apps.vendas.models import Venda
from core.decorators import grupo_gestor_required


@login_required
@grupo_gestor_required
def vendedores(request):
    """Lista e cadastra vendedores."""
    if request.method == "POST":
        form = VendedorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Vendedor cadastrado com sucesso.")
        else:
            for error in form.errors.values():
                messages.error(request, error[0], extra_tags="danger")

    return render(request, "vendedores/base.html", {"vendedores": Vendedor.objects.all()})


@login_required
@grupo_gestor_required
def delete_vendedor(request, id):
    """Exclui um vendedor."""
    get_object_or_404(Vendedor, id=id).delete()
    return redirect("vendedores:vendedores")


@login_required
@grupo_gestor_required
def edit_vendedor(request, id):
    """Exibe os detalhes de um vendedor e suas vendas."""
    vendedor = get_object_or_404(Vendedor, id=id)
    vendas = Venda.objects.filter(vendedor=vendedor)
    return render(request, "vendedores/base_vendedor.html", {"vendedor": vendedor, "vendas": vendas})


@login_required
@grupo_gestor_required
def update_vendedor(request, id):
    """Atualiza os dados de um vendedor."""
    vendedor = get_object_or_404(Vendedor, id=id)
    vendedor.nome = request.POST.get("nome_vendedor")
    vendedor.ativo = request.POST.get("ativo") == "on"
    vendedor.save()
    return redirect("vendedores:vendedores")
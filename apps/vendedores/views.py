from django.contrib import messages
from django.shortcuts import redirect, render
from .models import Vendedor
from apps.vendas.models import Venda

# Create your views here.


def vendedores(request):
    template_name = "vendedores/base.html"
    if request.method == "POST":
        ativo = request.POST.get("ativo")
        if ativo == "on":
            ativo = True
        else:
            ativo = False
        vendedores = Vendedor.objects.create(
            nome=request.POST.get("nome_vendedor"),
            ativo=ativo,
        )
        vendedores.save()
        messages.success(request, "Vendedor cadastrado com sucesso")
    vendedores = Vendedor.objects.all()

    return render(
        request, template_name=template_name, context={"vendedores": vendedores}
    )


def delete_vendedor(request, id):
    vendedor = Vendedor.objects.get(id=id)
    vendedor.delete()
    return redirect("vendedores:vendedores")


def edit_vendedor(request, id):
    vendedor = Vendedor.objects.get(id=id)
    vendas = Venda.objects.filter(
        vendedor=vendedor
    )  # Assume que a relação é feita via campo 'vendedor' na tabela Venda
    template_name = "vendedores/base_vendedor.html"
    return render(
        request,
        template_name=template_name,
        context={"vendedor": vendedor, "vendas": vendas},
    )


def update_vendedor(request, id):
    vendedor = Vendedor.objects.get(id=id)
    vendedor.nome = request.POST.get("nome_vendedor")
    ativo = request.POST.get("ativo")
    if ativo == "on":
        ativo = True
    else:
        ativo = False
    vendedor.ativo = ativo
    vendedor.save()
    return redirect("vendedores:vendedores")

from django.contrib import messages
from django.shortcuts import render
from .models import Vendedor

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

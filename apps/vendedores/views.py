from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from .models import Vendedor
from apps.vendas.models import Venda
from core.decorators import grupo_gestor_required
@grupo_gestor_required
def vendedores(request):
    """Lista e cadastra vendedores."""
    if request.method == "POST":
        nome = request.POST.get("nome_vendedor")
        cpf = request.POST.get("cpf_vendedor", "").strip()
        ativo = request.POST.get("ativo") == "on"
        
        if not cpf.isdigit() or len(cpf) != 11:
            messages.error(request, "O CPF deve conter exatamente 11 dígitos numéricos.", extra_tags="danger")
        elif Vendedor.objects.filter(cpf=cpf).exists():
            messages.error(request, "Já existe um vendedor com este CPF.", extra_tags="danger")
        else:
            Vendedor.objects.create(nome=nome, cpf=cpf, ativo=ativo)
            messages.success(request, "Vendedor cadastrado com sucesso.")
    
    return render(request, "vendedores/base.html", {"vendedores": Vendedor.objects.all()})
@grupo_gestor_required
def delete_vendedor(request, id):
    """Exclui um vendedor."""
    get_object_or_404(Vendedor, id=id).delete()
    return redirect("vendedores:vendedores")
@grupo_gestor_required
def edit_vendedor(request, id):
    """Exibe os detalhes de um vendedor e suas vendas."""
    vendedor = get_object_or_404(Vendedor, id=id)
    vendas = Venda.objects.filter(vendedor=vendedor)
    return render(request, "vendedores/base_vendedor.html", {"vendedor": vendedor, "vendas": vendas})
@grupo_gestor_required
def update_vendedor(request, id):
    """Atualiza os dados de um vendedor."""
    vendedor = get_object_or_404(Vendedor, id=id)
    vendedor.nome = request.POST.get("nome_vendedor")
    vendedor.ativo = request.POST.get("ativo") == "on"
    vendedor.save()
    return redirect("vendedores:vendedores")
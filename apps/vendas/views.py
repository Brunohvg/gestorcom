from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.utils.dateparse import parse_date
from django.utils.timezone import now
from .models import Venda, Vendedor

from django.contrib.auth.decorators import user_passes_test

def is_caixa(user):
    return user.groups.filter(name='caixa').exists()



def _buscar_vendas():
    """Retorna o contexto com vendas do dia e vendedores cadastrados."""
    hoje = now().date()
    return {
        "vendedores": Vendedor.objects.all(),
        "vendas": Venda.objects.filter(data_venda=hoje),
    }
 
def vendas(request):
    return (
        registrar_venda(request) if request.method == "POST" else render(request, "vendas/base.html", _buscar_vendas())
    )

@user_passes_test(is_caixa)
def registrar_venda(request):
    """Registra uma nova venda após validar os dados."""
    vendedor_id = request.POST.get("vendedor")
    valor = request.POST.get("valor")
    data_str = request.POST.get("data_venda")
    
    if not all([vendedor_id, valor, data_str]):
        return JsonResponse({"message": "Dados inválidos!"}, status=400)

    try:
        # Remover caracteres não numéricos, exceto vírgulas e pontos
        valor = valor.replace("R$", "").replace("\xa0", "").strip()  # Remove espaço invisível
        valor = valor.replace(".", "").replace(",", ".")  # Remove separador de milhar e ajusta decimal
        valor = float(valor)

        data_venda = parse_date(data_str)
        vendedor = get_object_or_404(Vendedor, id=vendedor_id)
        Venda.objects.create(vendedor=vendedor, valor_total=valor, data_venda=data_venda)

        return render(request, "vendas/base.html", _buscar_vendas())

    except (ValueError, TypeError):
        return JsonResponse({"message": "Erro ao processar os valores!"}, status=400)
    except Exception as e:
        return JsonResponse({"message": f"Erro interno: {str(e)}"}, status=500)
@user_passes_test(is_caixa)

def editar_venda(request, venda_id):
    """Edita uma venda existente, ajustando o valor total e a comissão."""
    venda = get_object_or_404(Venda, id=venda_id)
    
    if request.method == "POST":
        novo_valor = request.POST.get("valor_venda")
        
        try:



            novo_valor = novo_valor.replace("R$", "").replace("\xa0", "").strip()  # Remove espaço invisível
            novo_valor = novo_valor.replace(".", "").replace(",", ".")  # Remove separador de milhar e ajusta decimal
            novo_valor = float(novo_valor)
            # Remove qualquer caractere que não seja número, vírgula ou ponto
           
            venda.valor_total = novo_valor
            venda.valor_comissao = novo_valor * 0.01
            venda.save()
            
            return redirect("vendedores:edit_vendedor", venda.vendedor.id)
        
        except (ValueError, TypeError):
            return JsonResponse({"message": "Erro ao processar os valores!"}, status=400)
    
    return render(request, "vendas/base.html", {"venda": venda, "vendedor": venda.vendedor})
@user_passes_test(is_caixa)

def excluir_venda(request, venda_id):
    """Exclui uma venda com segurança."""
    get_object_or_404(Venda, id=venda_id).delete()
    return render(request, "vendas/base.html", _buscar_vendas())

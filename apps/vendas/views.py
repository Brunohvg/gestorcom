from django.shortcuts import render
from .models import Venda, Vendedor
from django.http import JsonResponse
from django.utils.dateparse import parse_date


def vendas(request):
    if request.method == "POST":
        vendedor_id = request.POST.get("vendedor")
        valor = request.POST.get("valor")
        data_str = request.POST.get("data_venda")  # Usando o nome correto do campo

        try:
            # Convertendo o valor para float
            valor = float(valor.replace("R$", "").replace(",", ".").strip())

            # Convertendo a data para o formato correto
            data = parse_date(data_str)

            # Obtendo o vendedor
            vendedor = Vendedor.objects.get(id=vendedor_id)

            # Criando a venda
            venda = Venda(
                vendedor=vendedor,
                valor_total=valor,
                data_venda=data,  # Usando o campo correto 'data_venda'
            )
            venda.save()

            vendedores = Vendedor.objects.all()
            context = {"vendedores": vendedores}
            return render(request, "vendas/base.html", context)

        # return JsonResponse({"message": "Venda registrada com sucesso!"})

        except Exception as e:
            print(f"Erro: {e}")
            return JsonResponse({"message": "Erro ao registrar a venda!"}, status=400)

    vendedores = Vendedor.objects.all()
    context = {"vendedores": vendedores}
    return render(request, "vendas/base.html", context)

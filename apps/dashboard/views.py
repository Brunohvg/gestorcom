from django.shortcuts import render
from .models import RelatorioComissao
from apps.vendedores.models import Vendedor
from django.db.models import Sum, Q
from apps.vendas.models import Venda
from django.utils import timezone


from django.contrib.auth.decorators import user_passes_test

def is_caixa(user):
    return user.groups.filter(name='gestor').exists()


@user_passes_test(is_caixa)
def dashboard(request):
    mes_atual = timezone.now().month
    ano_atual = timezone.now().year
    years = [2023, 2024, ano_atual]

    # Pega o mês e ano do request, se fornecido
    mes_selecionado = request.GET.get('mes', mes_atual)
    ano_selecionado = request.GET.get('ano', ano_atual)

    # Verifica se o ano selecionado está vazio e define como o ano atual
    if not ano_selecionado:
        ano_selecionado = ano_atual

    top_vendedores = Vendedor.objects.annotate(
        total_vendas_calc=Sum(
            'vendas__valor_total',
            filter=Q(vendas__data_venda__month=mes_selecionado) & Q(vendas__data_venda__year=ano_selecionado)
        )
    ).order_by('-total_vendas_calc')[:5]

    # Obtém os últimos 5 relatórios
    relatorios = RelatorioComissao.objects.all()

    # Obtém as últimas vendas
    ultimas_vendas = Venda.objects.order_by('-data_venda')[:5]

    # Total de Vendas e Comissões
    total_vendas = Venda.objects.aggregate(total=Sum('valor_total'))['total'] or 0
    total_comissoes = RelatorioComissao.objects.aggregate(total=Sum('total_comissao'))['total'] or 0

    # Passa o mês e ano selecionados para o contexto
    context = {
        'relatorios': relatorios,
        'top_vendedores': top_vendedores,
        'ultimas_vendas': ultimas_vendas,
        'total_vendas': total_vendas,
        'total_comissoes': total_comissoes,
        'mes_selecionado': mes_selecionado,
        'ano_selecionado': ano_selecionado,
        'years': years
    }

    return render(request, 'dashboard/base.html', context)
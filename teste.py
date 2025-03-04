from django.shortcuts import render
from .apps.dashboard.models import RelatorioComissao
from apps.vendedores.models import Vendedor
from django.db.models import Sum, Q
from apps.vendas.models import Venda
from django.utils import timezone

def dashboard(request):
    # Definindo o ano atual
    ano_atual = timezone.now().year
    anos = [ano_atual - i for i in range(5)]  # Últimos 5 anos

    # Pega o mês e ano do request, se fornecido
    mes_selecionado = request.GET.get('mes', timezone.now().month)
    ano_selecionado = request.GET.get('ano', ano_atual)

    # Garantindo que o ano selecionado seja tratado como inteiro
    ano_selecionado = int(ano_selecionado)

    # Obtendo os top vendedores
    top_vendedores = Vendedor.objects.annotate(
        total_vendas_calc=Sum(
            'vendas__valor_total',
            filter=Q(vendas__data_venda__month=mes_selecionado) & Q(vendas__data_venda__year=ano_selecionado)
        )
    ).order_by('-total_vendas_calc')[:5]

    # Filtra relatórios com base no mês e ano selecionados
    relatorios = RelatorioComissao.objects.filter(
        periodo_inicio__month=mes_selecionado,
        periodo_inicio__year=ano_selecionado
    )

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
        'years': anos,
    }

    return render(request, 'dashboard/base.html', context)
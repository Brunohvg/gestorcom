from django.shortcuts import render
from django.db.models import Sum, Q
from django.utils import timezone
from core.decorators import grupo_gestor_required

from .models import RelatorioComissao
from apps.vendedores.models import Vendedor
from apps.vendas.models import Venda

def get_selected_period(request, default_month, default_year):
    """
    Retorna o mês e o ano selecionados a partir dos parâmetros GET.
    Em caso de erro na conversão, utiliza os valores padrão.
    """
    try:
        mes = int(request.GET.get('mes', default_month))
    except (ValueError, TypeError):
        mes = default_month

    try:
        ano = int(request.GET.get('ano', default_year))
    except (ValueError, TypeError):
        ano = default_year

    return mes, ano

@grupo_gestor_required
def dashboard(request):
    now = timezone.now()
    mes_atual = now.month
    ano_atual = now.year
    anos_disponiveis = [2023, 2024, ano_atual]

    # Obtém os parâmetros de período
    mes_selecionado, ano_selecionado = get_selected_period(request, mes_atual, ano_atual)

    # Top vendedores filtrados pelo mês/ano selecionados
    top_vendedores = Vendedor.objects.annotate(
        total_vendas_calc=Sum(
            'vendas__valor_total',
            filter=Q(vendas__data_venda__month=mes_selecionado) &
                   Q(vendas__data_venda__year=ano_selecionado)
        )
    ).order_by('-total_vendas_calc')[:5]

    # Relatórios de comissão filtrados pelo mês/ano
    relatorios = RelatorioComissao.objects.filter(
        periodo_inicio__month=mes_selecionado,
        periodo_inicio__year=ano_selecionado
    )

    # Total de vendas do período
    total_vendas = Venda.objects.filter(
        data_venda__month=mes_selecionado,
        data_venda__year=ano_selecionado
    ).aggregate(total=Sum('valor_total'))['total'] or 0

    # Total de comissão do período
    total_comissoes = RelatorioComissao.objects.filter(
        periodo_inicio__month=mes_selecionado,
        periodo_inicio__year=ano_selecionado
    ).aggregate(total=Sum('total_comissao'))['total'] or 0

    # Cálculo do ticket médio
    vendas_count = Venda.objects.filter(
        data_venda__month=mes_selecionado,
        data_venda__year=ano_selecionado
    ).count()
    ticket_medio = total_vendas / vendas_count if vendas_count > 0 else 0

    # Cálculo do comparativo: total de vendas do mês atual versus mês anterior
    if mes_selecionado == 1:
        mes_anterior = 12
        ano_anterior = ano_selecionado - 1
    else:
        mes_anterior = mes_selecionado - 1
        ano_anterior = ano_selecionado

    total_vendas_anterior = Venda.objects.filter(
        data_venda__month=mes_anterior,
        data_venda__year=ano_anterior
    ).aggregate(total=Sum('valor_total'))['total'] or 0

    if total_vendas_anterior > 0:
        comparativo_vendas = ((total_vendas - total_vendas_anterior) / total_vendas_anterior) * 100
    else:
        comparativo_vendas = 0

    context = {
        'relatorios': relatorios,
        'top_vendedores': top_vendedores,
        'total_vendas': total_vendas,
        'total_comissoes': total_comissoes,
        'mes_selecionado': mes_selecionado,
        'ano_selecionado': ano_selecionado,
        'years': anos_disponiveis,
        'ticket_medio': ticket_medio,
        'comparativo_vendas': comparativo_vendas,
    }

    return render(request, 'dashboard/base.html', context)

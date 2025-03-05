from django.shortcuts import render
from apps.dashboard.models import RelatorioComissao
from apps.vendedores.models import Vendedor
from django.db.models import Sum, Q
from apps.vendas.models import Venda
from django.utils import timezone
from core.decorators import grupo_gestor_required

@grupo_gestor_required
def dashboard(request):
    mes_atual = timezone.now().month
    ano_atual = timezone.now().year
    years = [2023, 2024, ano_atual]

    # Pega o mês e ano do request, se fornecido
    mes_selecionado = request.GET.get('mes', str(mes_atual).zfill(2))  # Preenche com zero à esquerda
    ano_selecionado = request.GET.get('ano', ano_atual)

    # Verifica se o ano selecionado está vazio e define como o ano atual
    if not ano_selecionado:
        ano_selecionado = ano_atual

    # Filtra os vendedores com base no mês e ano selecionados
    top_vendedores = Vendedor.objects.annotate(
        total_vendas_calc=Sum(
            'vendas__valor_total',
            filter=Q(vendas__data_venda__month=mes_selecionado) & Q(vendas__data_venda__year=ano_selecionado)
        )
    ).order_by('-total_vendas_calc')[:5]

    # Obtém os últimos 5 relatórios
    relatorios = RelatorioComissao.objects.filter(
        periodo_inicio__year=ano_selecionado,
        periodo_inicio__month=mes_selecionado
    )

    # Total de Vendas e Comissões
    total_vendas_mes = Venda.objects.filter(
        data_venda__month=mes_selecionado,
        data_venda__year=ano_selecionado
    ).aggregate(total=Sum('valor_total'))['total'] or 0

    total_comissoes = relatorios.aggregate(total=Sum('total_comissao'))['total'] or 0

    # Passa o mês e ano selecionados para o contexto
    context = {
        'relatorios': relatorios,
        'top_vendedores': top_vendedores,
        'total_vendas_mes': total_vendas_mes,
        'total_comissoes': total_comissoes,
        'mes_selecionado': mes_selecionado,
        'ano_selecionado': ano_selecionado,
        'years': years
    }

    return render(request, 'dashboard/base.html', context)
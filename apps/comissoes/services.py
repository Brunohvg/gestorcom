from decimal import Decimal

from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import (
    Competencia,
    ConfiguracaoComissao,
    FaixaComissao,
    HistoricoTaxaComissao,
)


# ---------------------------------------------------------------------------
# Resolução de Taxa (4 camadas)
# ---------------------------------------------------------------------------

def obter_taxa(vendedor, valor_total=Decimal("0.00")):
    """
    Retorna a taxa de comissão aplicável, seguindo prioridade:
    1. Faixas escalonadas do vendedor
    2. Taxa fixa do vendedor
    3. Faixas escalonadas globais
    4. Taxa padrão global (ConfiguracaoComissao)
    """
    # 1. Faixas do vendedor
    faixas_vendedor = FaixaComissao.objects.filter(vendedor=vendedor)
    if faixas_vendedor.exists():
        for faixa in faixas_vendedor:
            if faixa.contem_valor(valor_total):
                return faixa.taxa

    # 2. Taxa fixa do vendedor
    if vendedor.taxa_comissao is not None:
        return vendedor.taxa_comissao

    # 3. Faixas globais
    faixas_globais = FaixaComissao.objects.filter(vendedor__isnull=True)
    if faixas_globais.exists():
        for faixa in faixas_globais:
            if faixa.contem_valor(valor_total):
                return faixa.taxa

    # 4. Fallback: taxa padrão
    return ConfiguracaoComissao.get().taxa_padrao


def calcular_comissao(valor_total, taxa):
    """Calcula o valor da comissão dado valor e taxa (%)."""
    return (valor_total * taxa) / Decimal("100")


# ---------------------------------------------------------------------------
# Histórico de Alterações
# ---------------------------------------------------------------------------

def registrar_alteracao_taxa(vendedor, taxa_anterior, taxa_nova, usuario, motivo=""):
    """Registra alteração de taxa no histórico auditável."""
    return HistoricoTaxaComissao.objects.create(
        vendedor=vendedor,
        taxa_anterior=taxa_anterior,
        taxa_nova=taxa_nova,
        alterado_por=usuario,
        motivo=motivo,
    )


# ---------------------------------------------------------------------------
# Transições de Status da Competência
# ---------------------------------------------------------------------------

TRANSICOES_VALIDAS = {
    Competencia.Status.ABERTA: [Competencia.Status.EM_CONFERENCIA],
    Competencia.Status.EM_CONFERENCIA: [
        Competencia.Status.ABERTA,
        Competencia.Status.ENVIADA,
    ],
    Competencia.Status.ENVIADA: [
        Competencia.Status.EM_CONFERENCIA,
        Competencia.Status.APROVADA,
    ],
    Competencia.Status.APROVADA: [Competencia.Status.PAGA],
    Competencia.Status.PAGA: [],
}


def transicionar_status(competencia, novo_status, usuario, justificativa=None):
    """Executa transição de status com validação e registro de auditoria."""
    status_atual = competencia.status
    permitidos = TRANSICOES_VALIDAS.get(status_atual, [])

    if novo_status not in permitidos:
        raise ValidationError(
            f"Transição de '{competencia.get_status_display()}' "
            f"para '{Competencia.Status(novo_status).label}' não é permitida."
        )

    agora = timezone.now()

    if novo_status == Competencia.Status.ENVIADA:
        competencia.enviada_em = agora
        competencia.enviada_por = usuario
    elif novo_status == Competencia.Status.APROVADA:
        competencia.aprovada_em = agora
        competencia.aprovada_por = usuario
    elif novo_status == Competencia.Status.PAGA:
        competencia.paga_em = agora
        competencia.paga_por = usuario

    competencia.status = novo_status
    competencia.save()
    return competencia

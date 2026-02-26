from django.contrib import admin

from .models import (
    Competencia,
    ComissaoVendedor,
    ConfiguracaoComissao,
    FaixaComissao,
    HistoricoTaxaComissao,
)


@admin.register(ConfiguracaoComissao)
class ConfiguracaoComissaoAdmin(admin.ModelAdmin):
    list_display = ["taxa_padrao", "atualizado_em", "atualizado_por"]

    def has_add_permission(self, request):
        return not ConfiguracaoComissao.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(FaixaComissao)
class FaixaComissaoAdmin(admin.ModelAdmin):
    list_display = ["vendedor", "valor_minimo", "valor_maximo", "taxa"]
    list_filter = ["vendedor"]
    search_fields = ["vendedor__nome"]


@admin.register(HistoricoTaxaComissao)
class HistoricoTaxaComissaoAdmin(admin.ModelAdmin):
    list_display = ["vendedor", "taxa_anterior", "taxa_nova", "alterado_por", "alterado_em"]
    list_filter = ["alterado_em", "vendedor"]
    readonly_fields = ["vendedor", "taxa_anterior", "taxa_nova", "alterado_por", "alterado_em", "motivo"]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(Competencia)
class CompetenciaAdmin(admin.ModelAdmin):
    list_display = ["__str__", "status", "criada_em"]
    list_filter = ["status", "ano"]
    search_fields = ["ano", "mes"]
    readonly_fields = ["criada_em", "atualizada_em"]


@admin.register(ComissaoVendedor)
class ComissaoVendedorAdmin(admin.ModelAdmin):
    list_display = ["vendedor", "competencia", "total_vendas", "total_comissao", "comissao_final"]
    list_filter = ["competencia__status", "competencia__ano"]
    search_fields = ["vendedor__nome"]

from django.urls import path
from ..vendas import views

app_name = "vendas"
urlpatterns = [
    path("vendas/", views.vendas, name="vendas"),
    path("excluir/<int:venda_id>", views.excluir_venda, name="excluir_venda"),
    path("editar/<int:venda_id>", views.editar_venda, name="editar_venda"),
    #path("editar/<int:venda_id>", views.editar_venda, name="editar_venda"),
    path("editar-venda/<int:venda_id>/", views.editar_venda, name="editar_venda"),

]

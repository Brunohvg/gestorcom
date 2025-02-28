from django.urls import path
from ..vendas import views

app_name = "vendas"
urlpatterns = [
    path("vendas/", views.vendas, name="vendas"),
]

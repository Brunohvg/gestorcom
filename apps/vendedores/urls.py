from django.urls import path
from ..vendedores import views

app_name = "vendedores"
urlpatterns = [
    path("register/", views.vendedores, name="vendedores"),
    path("vendedores/", views.vendedores, name="vendedores"),
    path("edit/<int:id>", views.edit_vendedor, name="edit_vendedor"),
    path("delete/<int:id>", views.delete_vendedor, name="delete_vendedor"),
]

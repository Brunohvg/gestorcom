from django.urls import path
from ..vendedores import views

app_name = "vendedores"
urlpatterns = [
    path("register/", views.vendedores, name="vendedores"),
]

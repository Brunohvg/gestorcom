from django.urls import path
from ..usuarios import views

app_name = 'usuarios'
urlpatterns = [
    path('login/', views.login, name='usuarios'),
]
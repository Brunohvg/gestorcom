from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages


def login_views(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)
            if user.groups.filter(name="caixa").exists():
                return redirect("vendas:vendas")
            return redirect("dashboard:dashboard")
        else:
            messages.error(request, "Nome de usuário ou senha inválidos.")

    return render(request, "usuarios/base.html")


def logout_view(request):
    auth_logout(request)
    messages.success(request, "Sessão encerrada com sucesso.")
    return redirect("usuarios:login")

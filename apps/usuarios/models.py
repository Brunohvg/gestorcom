from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login
from django.contrib import messages

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Autentica o usuário
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Se a autenticação for bem-sucedida, faz o login
            auth_login(request, user)
            return redirect('home')  # Redirecione para a página inicial ou para uma página específica
        else:
            # Se não autenticado, exibe uma mensagem de erro
            messages.error(request, "Nome de usuário ou senha inválidos.")
    
    return render(request, 'usuarios/base.html')

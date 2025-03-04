from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login
from django.contrib import messages

def login_views(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Autentica o usuário
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Se a autenticação for bem-sucedida, faz o login
            auth_login(request, user)

            # Verifica se o usuário pertence a algum grupo específico
            if user.groups.filter(name='caixa').exists():
                # Redireciona para a página de vendas se o usuário for do grupo 'caixa'
                return redirect('vendas:vendas')
            else:
                # Redireciona para a página inicial ou para outra página específica
                return redirect('dashboard:dashboard')  

        else:
            # Se não autenticado, exibe uma mensagem de erro
            messages.error(request, "Nome de usuário ou senha inválidos.")
    
    return render(request, 'usuarios/base.html')

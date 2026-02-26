from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def grupo_caixa_required(view_func):
    """Restringe acesso a usuários do grupo 'caixa' ou 'gestor'."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and (
            request.user.groups.filter(name="caixa").exists() or 
            request.user.groups.filter(name="gestor").exists()
        ):
            return view_func(request, *args, **kwargs)
        messages.error(request, "Acesso não permitido!")
        return redirect("/login")
    return wrapper


def grupo_gestor_required(view_func):
    """Restringe acesso a usuários do grupo 'gestor'."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.groups.filter(name="gestor").exists():
            return view_func(request, *args, **kwargs)
        messages.error(request, "Acesso não permitido!")
        return redirect("/login")
    return wrapper


def grupo_financeiro_required(view_func):
    """Restringe acesso a usuários do grupo 'financeiro'."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.groups.filter(name="financeiro").exists():
            return view_func(request, *args, **kwargs)
        messages.error(request, "Acesso não permitido!")
        return redirect("/login")
    return wrapper
from django.shortcuts import redirect
from django.contrib import messages

def grupo_caixa_required(view_func):
    """Decorator que restringe acesso a usuários do grupo 'caixa'."""
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.groups.filter(name="caixa").exists():
            return view_func(request, *args, **kwargs)
        
        messages.error(request, "Acesso não permitido!")
        return redirect("/login")
    
    return wrapper

def grupo_gestor_required(view_func):
    """Decorator que restringe acesso a usuários do grupo 'gestor'."""
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.groups.filter(name="gestor").exists():
            return view_func(request, *args, **kwargs)
        
        messages.error(request, "Acesso não permitido!")
        return redirect("/login")
    
    return wrapper
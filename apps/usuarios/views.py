from django.shortcuts import render

# Create your views here.
def login(request):
    template_name = 'usuarios/base.html'
    print(request.POST.get('user_name'))
    return render(request, template_name=template_name)


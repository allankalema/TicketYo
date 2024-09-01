from django.shortcuts import render

def index(request):
    return render(request, 'frontend/base.html')


def universal_login_view(request):
    return render(request, 'frontend/universal_login.html')
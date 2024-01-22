from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.contrib.messages import constants
from django.contrib import messages
from django.contrib import auth
# Create your views here.

def cadastro(request):
    
    if request.method == "GET":
        
        return render(request, 'cadastro.html')
    
    elif request.method == "POST":
        username = request.POST.get('username')
        senha = request.POST.get('senha')
        confirmar_senha = request.POST.get('confirmar_senha')
        
        if not senha == confirmar_senha:
            messages.add_message(request, constants.ERROR, 'A senha e a confirmação da senha são discrepantes!!')
            return redirect('/usuarios/cadastro')
        
        user = User.objects.filter(username=username)
        
        if user.exists():
            messages.add_message(request, constants.ERROR, 'Usuário existente!!')
            return redirect('/usuarios/cadastro')
        
        try:
            User.objects.create_user(
                username=username,
                password=senha,
        )
            return redirect('/usuarios/login')
        
        except:
            messages.add_message(request, constants.ERROR, 'Erro interno do servidor!!')
            return redirect('/usuarios/cadastro')

def logar(request):
    if request.method == "GET":
        return render(request,'login.html')
    
    elif request.method == "POST":
        username = request.POST.get('username')
        senha = request.POST.get('senha')
        
        user = auth.authenticate(request, username=username, password=senha)
        # O authenticate serve para verificar no banco auth_user, existe um usuário com a senha colocada no banco. 
        # Se sim, ele retorna o username. Se não, ele retorna None. De modo que não precisa fazer todo um esquema
        # de ifs e elifs
        
        if user:
            auth.login(request, user) #login vai permitir o acesso do usuário ao sistema através do seu user!
            messages.add_message(request, constants.SUCCESS, 'Logado!!')
            return redirect('/flashcard/novo_flashcard')
        else:
            messages.add_message(request, constants.ERROR, 'Username ou senha incorretas!!')
            return redirect('/usuarios/logar')
        
def logout(request):
    auth.logout(request) #logout vai desligar o usuário do sistema
    return redirect('/usuarios/logar')
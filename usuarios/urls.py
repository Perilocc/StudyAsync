from django.urls import path
from .import views

urlpatterns = [
    path('cadastro/', views.cadastro, name = "cadastro"), #rota para o cadastro de usuário
    path('logar/', views.logar, name="login"), #rota para o login do usuario
    path('logout/', views.logout, name="logout"), #rota do logout do sistema
]
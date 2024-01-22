from django.urls import path
from . import views


urlpatterns = [
    path('novo_flashcard/', views.novo_flashcard, name='novo_flashcard'), # url para acessar o html de new flashcard
    path('deletar_flashcard/<int:id>', views.deletar_flashcard, name='deletar_flashcard'), #url para deletar flashcard pelo id
    path('iniciar_desafio/', views.iniciar_desafio, name='iniciar_desafio'), #url do desafio com flashcards
    path('listar_desafio/', views.listar_desafio, name='listar_desafio'),
    path('desafio/<int:id>/', views.desafio, name='desafio'),
    path('responder_flashcard/<int:id>', views.responder_flashcard, name='responder_flashcard'),
    path('relatorio/<int:id>', views.relatorio, name='relatorio'),
]
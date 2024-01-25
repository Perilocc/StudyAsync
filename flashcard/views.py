from django.shortcuts import render, redirect
from .models import Categoria, Flashcard, Desafio, FlashcardDesafio
from django.contrib.messages import constants
from django.contrib import messages
from django.http import HttpResponse, Http404


# Create your views here.

def novo_flashcard(request):
    if not request.user.is_authenticated: #verifica se o usuário está autenticado com algum user existente. se não, volta para tela de login
        return redirect('/usuarios/logar/')
    
    if request.method == "GET":
        categorias = Categoria.objects.all() #Pega todas as categorias do banco de dados
        dificuldades = Flashcard.DIFICULDADE_CHOICES #Pega do banco de dados as dificuldades possíveis 
        flashcards = Flashcard.objects.filter(user=request.user) #Pega todas as flashcards criadas pelo usuário autenticado
        
        categoria_filtrar = request.GET.get('categoria') # Supondo que cliquei na categoria matemática, ele vai ver no html que está nessa categoria pelo name e vai puxar todas com msm nome
        dificuldade_filtrar = request.GET.get('dificuldade')
        
        if categoria_filtrar:
            flashcards = flashcards.filter(categoria__id=categoria_filtrar) # Aqui é só para garantir que o usuario colocou categoria, se não, puxa todos os flashcards do user
            
        if dificuldade_filtrar:
            flashcards = flashcards.filter(dificuldade=dificuldade_filtrar)
        
        return render(request, 'novo_flashcard.html', {'categorias': categorias, 'dificuldades': dificuldades, 'flashcards': flashcards})
    
    elif request.method == "POST":
        pergunta = request.POST.get('pergunta')
        resposta = request.POST.get('resposta')
        categoria = request.POST.get('categoria')
        dificuldade = request.POST.get('dificuldade')
        
        if len(pergunta.strip()) == 0 or len(resposta.strip()) == 0:
            messages.add_message(request, constants.ERROR, "Preencha os campos de pergunta e resposta!!")
            return redirect('/flashcard/novo_flashcard/')
        
        flashcard = Flashcard(
            user=request.user,
            pergunta=pergunta,
            resposta=resposta,
            categoria_id=categoria,
            dificuldade=dificuldade,
        ) #Pega as informações e armazena em flashcard
        
        flashcard.save() #Salva no banco de dados
        messages.add_message(request, constants.SUCCESS, 'Flashcard Criado com Sucesso!!')
        return redirect('/flashcard/novo_flashcard/')

def deletar_flashcard(request, id):
        flashcard = Flashcard.objects.get(id=id) #get retorna apenas um valor, que no caso é o id que é primary key
        flashcard.delete()
        messages.add_message(request, constants.SUCCESS, 'Flashcard deletado com sucesso!!')
        return redirect('/flashcard/novo_flashcard/')
    
def iniciar_desafio(request):
    if request.method == "GET":
        categorias = Categoria.objects.all() #Pega todas as categorias do banco de dados
        dificuldades = Flashcard.DIFICULDADE_CHOICES #Pega do banco de dados as dificuldades possíveis 
        return render(request, 'iniciar_desafio.html', {'categorias': categorias, 'dificuldades': dificuldades})
    
    elif request.method == "POST":
        titulo = request.POST.get('titulo')
        categorias = request.POST.getlist('categoria') #getlist pega todos a lista de dados
        dificuldade = request.POST.get('dificuldade')
        qtd_perguntas = request.POST.get('qtd_perguntas')
        
        desafio = Desafio(
            user=request.user,
            titulo=titulo,
            quantidade_perguntas=qtd_perguntas,
            dificuldade=dificuldade, #O que está na esquerda leva o nome respectivo no banco de dados, e direita o nome que tá no request acima
        )
        
        desafio.save() # Os atributos Many to Many fields não podem ser salvas junto dos dados únicos. Logo tem que salvar primeiro e depois adicionar as categorias e os flashcards
        
        for categoria in categorias:
            desafio.categoria.add(categoria)
            
        flashcards = (Flashcard.objects.filter(user=request.user) #filtra os flashcards apenas desse user
        .filter(dificuldade=dificuldade) #filtra os flashcards da dificuldade escolhida
        .filter(categoria_id__in=categorias) #filtra as categorias que os ids estejam numa lista de categorias ex: categorias = request.POST.getlist('categoria')
        .order_by('?') #order by ? pega aleatório
        )
        
        n_flashcards = flashcards.count()

        if n_flashcards < int(qtd_perguntas):
            messages.add_message(request, constants.ERROR, 'Quantidade de questões superior a quantidade de flashcards!!')
            return redirect('/flashcard/iniciar_desafio/')
        
        flashcards = flashcards[:int(qtd_perguntas)]
        
        for flashcard in flashcards:
            flashcard_desafio = FlashcardDesafio(
                flashcard=flashcard,
            )
            
            flashcard_desafio.save()
            desafio.flashcards.add(flashcard_desafio)
        
        desafio.save()
        
        return redirect('/flashcard/listar_desafio/')
            
def listar_desafio(request):
    
    if request.method == "GET":
        desafios = Desafio.objects.filter(user=request.user)
        categorias = Categoria.objects.all()
        dificuldades = Flashcard.DIFICULDADE_CHOICES
        
        categoria_filtrar = request.GET.get('categoria')
        dificuldade_filtrar = request.GET.get('dificuldade')
        
        if categoria_filtrar:
            desafios = desafios.filter(categoria__id=categoria_filtrar)
            
        if dificuldade_filtrar:
            desafios = desafios.filter(dificuldade=dificuldade_filtrar)
            
        return render(request, 'listar_desafio.html', {'desafios': desafios, 'categorias': categorias, 'dificuldades': dificuldades})
    
def desafio(request, id):
    
    desafio = Desafio.objects.get(id=id)
    
    if not desafio.user == request.user:
        raise Http404()
    
    if request.method == "GET":
        
        acertos = desafio.flashcards.filter(respondido=True).filter(acertou=1).count()
        erros = desafio.flashcards.filter(respondido=True).filter(acertou=0).count()
        faltantes = desafio.flashcards.filter(respondido=False).count()
        
        return render(request, 'desafio.html', {'desafio': desafio, 'acertos': acertos, 'erros': erros, 'faltantes': faltantes})
    
def responder_flashcard(request, id):
    
    flashcard_desafio = FlashcardDesafio.objects.get(id=id)
    acertou = request.GET.get('acertou')
    desafio_id = request.GET.get('desafio_id')
    
    if not flashcard_desafio.flashcard.user == request.user:
        raise Http404()
    
    flashcard_desafio.respondido = True
    
    if acertou == "1":
        flashcard_desafio.acertou = True
    elif acertou == "0":
        flashcard_desafio.acertou = False
        
    flashcard_desafio.save()
    
    return redirect(f'/flashcard/desafio/{desafio_id}/')

def relatorio(request, id):
    
    desafio = Desafio.objects.get(id=id)
    acertos = desafio.flashcards.filter(respondido=True).filter(acertou=1).count()
    erros = desafio.flashcards.filter(respondido=True).filter(acertou=0).count()
    categorias = desafio.categoria.all()
    
    #dados para os gráficos do chart.js
    dados = [acertos, erros]
    
    dados_categorias = [categoria.nome for categoria in categorias]
    
    dados2 = []
    for categoria in categorias:
        dados2.append(desafio.flashcards.filter(flashcard__categoria=categoria).filter(acertou=True).count())
    
    return render(request, 'relatorio.html', {'desafio': desafio, 'dados': dados, 'dados_categorias': dados_categorias, 'dados2': dados2})
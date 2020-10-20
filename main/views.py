from time import mktime
from datetime import datetime
import unicodedata
from sklearn.metrics.pairwise import linear_kernel
from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd
import requests
import pprint
import random
import feedparser
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, forms
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.views.generic import CreateView, TemplateView
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.utils import timezone
# from django.core.urlresolvers import reverse_lazy
import hashlib

from .models import Preferencia, Noticia, Perfil, Fuente, Categoria

from .forms import SignUpForm


class articulo:
    '''
    Clase que contiene temporalmente cada artículo de noticias
    '''

    def __init__(self, article):
        h = hashlib.md5()
        h.update(article['title'].encode('utf-8'))
        self.id = int(h.hexdigest(), 16) % 10000000
        self.titulo = article['title']
        self.descripcion = article['description']
        self.url = article['url']
        self.urlImagen = article['urlToImage']
        self.fecha = article['publishedAt']
        self.autor = article['author']
        self.nombre = article['source']['name']


def extraerArticulos(feeds):
    '''
    Recibe una lista de feeds cada item de la lista tiene los atributos 'diario' y 'url'
    Devuelve un iterable conteniendo los objetos articulo obtenidos del feed
    '''
    for feed in feeds:
        # Lee el RSS contenido en el feed y obteien un diccionario donde cada entrada es un dato del artículo
        rss = feedparser.parse(feed['url'])
        for item in rss['entries']:
            article = dict()
            if 'title' in item:
                article['title'] = item['title']
                article['description'] = item['summary']
                article['url'] = item['link']
                article['urlToImage'] = '#'
                article['publishedAt'] = timezone.make_aware(datetime.strptime(
                    item['published'][5:25], '%d %b %Y %H:%M:%S'), timezone.get_default_timezone())  # convierte la hora en formato utc
                article['author'] = ''
                article['source'] = dict()
                article['source']['name'] = feed['diario']
                yield articulo(article)


def obtenerFuentes(categorias):
    articulos = []  # aqui se acumularan los objetos articulo
    # obtiene todas las fuentes de la base de datos
    # aqui se guardaran las fuentes en un diccionario por categorias
    todasFuentesCategoria = {}
    for categoria in categorias:
        # seleccion por un Foreign Key
        fuentes = Fuente.objects.filter(
            categoria__categoria=categoria['categoria']).values()
        articulosCategoria = list(extraerArticulos(fuentes))
        articulosCategoria.sort(key=lambda x: x.fecha, reverse=True)
        articulos = articulos + articulosCategoria
        todasFuentesCategoria.setdefault(
            categoria['categoria'], articulosCategoria)

    return articulos, todasFuentesCategoria


# devuelve el objeto artículo de una lista de artículo


def grabaNoticia(articulo):
    loquehay = Noticia.objects.filter(id_noticia=articulo.id)
    if len(loquehay) == 0:
        instancia = Noticia.objects.create(
            id_noticia=articulo.id,
            titulo=articulo.titulo,
            descripcion=articulo.descripcion,
            url=articulo.url,
            urlImagen=articulo.urlImagen,
            fecha=articulo.fecha,
            autor=articulo.autor,
            nombre=articulo.nombre,
        )
    else:
        instancia = loquehay.last()
    instancia.save()
    return instancia


def calculaDistancias():

    articulos.sort(key=lambda x: x.fecha, reverse=True)

    f = open("datos.csv", "w", encoding="utf-8")
    f.write('id,description\n')
    for articulo in articulos:
        linea = "" + str(articulo.id) + ",\"" + articulo.titulo + \
            "-" + articulo.descripcion + "\"\n"
        f.write(linea)
    f.close()

    def normalizatexto(texto):
        '''
        Normaliza el texto para evitar que caracteres extraños entren al conteo de palabras
        '''
        return unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').strip().lower()

    # Prepara el vector de puntajes para hacer las recomendaciones

    ds = pd.read_csv("datos.csv", usecols=[
                     "id", "description"], encoding="latin")

    tf = TfidfVectorizer(analyzer='word', ngram_range=(1, 3),
                         min_df=0, stop_words='english')
    tfidf_matrix = tf.fit_transform(ds['description'])

    cosine_similarities = linear_kernel(tfidf_matrix, tfidf_matrix)

    results = {}

    for idx, row in ds.iterrows():
        similar_indices = cosine_similarities[idx].argsort()[:-100:-1]
        similar_items = [(cosine_similarities[idx][i], ds['id'][i])
                         for i in similar_indices]

        results[row['id']] = similar_items[1:]

    return results


categorias = Categoria.objects.all().values()
articulos, todosXcategoria = obtenerFuentes(categorias)
results = calculaDistancias()


# def item(id):
#     return ds.loc[ds['id'] == id]['description'].tolist()[0].split(' - ')[0]


def recommend(item_id, num):
    recs = results[item_id][:num]
    return recs


class SignUpView(CreateView):
    '''
    Esto crea la vista que muestra el formulario sobrecargado que acepta el email en base al modelo Perfil
    '''
    model = Perfil
    form_class = SignUpForm

    # sobrecargamos la función que valida el formulario para que si se ha ingresado los datos correctos se permita el longin

    def form_valid(self, form):
        if form.is_valid():
            usuario = form.save()
            nombre_usuario = form.cleaned_data.get(
                'username')  # obtiene el nombre del usuario
            messages.success(
                self.request, f"Nueva Cuenta Creada : {nombre_usuario}")
            login(self.request, usuario)
            messages.info(
                self.request, f"Has sido logueado como {nombre_usuario}")
            return redirect("main:homepage")
        else:
            for msg in form.error_messages:
                messages.error(
                    self.request, f"{msg}: {form.error_messages[msg]}")
        return render(self.request, "main/perfil_form.html", {"form": form})

    def form_invalid(self, form):
        for msg in form.error_messages:
            messages.error(
                self.request, f"{form.error_messages[msg]}")
        return render(self.request, "main/perfil_form.html", {"form": form})


def perfiluser(request):
    usuario_actual = request.user
    consultaPreferencias = Preferencia.objects.filter(
        usuario=usuario_actual)
    return render(request, "main/bienvenida.html", {"news": consultaPreferencias, })


def recuperacion(request):
    return render(request, "main/recuperacion.html")


def usuariorec(request):
    return render(request, "main/usuariorec.html")


def categoria(request, nomcat=None):
    usuario_actual = request.user
    consultaPreferencias = Preferencia.objects.filter(
        usuario=usuario_actual)
    preferencias = [
        preferencia.id_noticia.id_noticia for preferencia in consultaPreferencias]

    return render(request, "main/inicio.html", {"news": todosXcategoria[nomcat], "categoria": nomcat, "activa": nomcat, "categorias": categorias, "preferencias": preferencias, })


def politica(request):
    # random.shuffle(articulosPolitica)
    usuario_actual = request.user
    consultaPreferencias = Preferencia.objects.filter(
        usuario=usuario_actual)
    preferencias = [
        preferencia.id_noticia.id_noticia for preferencia in consultaPreferencias]
    return render(request, "main/inicio.html", {"news": articulosPolitica, "categoria": "politica", "activa": "politica", "categorias": categorias, "preferencias": preferencias, })


def economia(request):
    # random.shuffle(articulosEconomia)
    usuario_actual = request.user
    consultaPreferencias = Preferencia.objects.filter(
        usuario=usuario_actual)
    preferencias = [
        preferencia.id_noticia.id_noticia for preferencia in consultaPreferencias]
    return render(request, "main/inicio.html", {"news": articulosEconomia, "categoria": "economia", "activa": "economia", "categorias": categorias, "preferencias": preferencias, })


def salud(request):
    # random.shuffle(articulosSalud)
    usuario_actual = request.user
    consultaPreferencias = Preferencia.objects.filter(
        usuario=usuario_actual)
    preferencias = [
        preferencia.id_noticia.id_noticia for preferencia in consultaPreferencias]
    return render(request, "main/inicio.html", {"news": articulosSalud, "categoria": "salud", "activa": "salud", "categorias": categorias, "preferencias": preferencias, })


def busqueda(request):
    usuario_actual = request.user
    consultaPreferencias = Preferencia.objects.filter(
        usuario=usuario_actual)
    preferencias = [
        preferencia.id_noticia.id_noticia for preferencia in consultaPreferencias]
    textobuscado = normalizatexto(request.GET['search'])
    articulosBusqueda = [
        articulo for articulo in articulos if textobuscado in normalizatexto(articulo.titulo)]
    return render(request, "main/inicio.html", {"news": articulosBusqueda, "categoria": "Busqueda", "activa": "Busqueda", "categorias": categorias, "preferencias": preferencias, })


def recomendados(request):
    usuario_actual = request.user
    consultaPreferencias = Preferencia.objects.filter(
        usuario=usuario_actual)
    preferencias = [
        preferencia.id_noticia.id_noticia for preferencia in consultaPreferencias]
    # print("Preferencias:", consultaPreferencias)
    if len(preferencias) == 0:  # si no hay preferencias, puede significar que nunca eligió nada o que no se ha logueado
        idUltimaNoticia = None
    else:
        # si hay preferencias previas elegimos la última como referencia para la consulta
        idUltimaNoticia = preferencias[-1]
    # si no hubo ultima noticia y el id elegido no está en el computo de resultados
    if idUltimaNoticia == None or not idUltimaNoticia in results:
        elegido = random.randint(0, len(articulos))
        id_elegido = articulos[elegido].id
    else:
        id_elegido = idUltimaNoticia
    recomendaciones = recommend(item_id=id_elegido, num=20)
    ids_recomendados = [item[1] for item in recomendaciones]
    articulosrecomendados = [
        articulo for articulo in articulos if articulo.id in ids_recomendados and not articulo.id in preferencias]
    # print("PREFERENCIAS", preferencias)
    # print("ARTICULO", [art.descripcion for art in articulosrecomendados])
    return render(request, "main/inicio.html", {"news": articulosrecomendados, "categoria": "recomendados", "activa": "recomendados", "categorias": categorias, "preferencias": preferencias, })


def check(request):
    def recuperaNoticia(articulos, idn):
        for articulo in articulos:
            if articulo.id == int(idn):
                return articulo
    noticia = request.POST['id']
    if noticia == '':
        return HttpResponse('')
    # check = request.POST['click']
    print("ID:", noticia)
    usuario = request.POST['usuario']
    consulta = Preferencia.objects.filter(
        usuario=usuario).filter(id_noticia=noticia)
    if (len(consulta) == 0):
        nuevanoticia = recuperaNoticia(
            articulos, noticia)  # obtiene el objeto noticia
        print("NOTICIA:", nuevanoticia)
        noticiagrabar = grabaNoticia(nuevanoticia)
        nuevocheck = Preferencia.objects.create(
            id_noticia=noticiagrabar, preferencia=True, usuario=usuario)
        nuevocheck.save()
        return HttpResponse('true')
    consulta.delete()
    return HttpResponse('false')


def registro(request):
    form = UserCreationForm()
    forms.CharField
    if request.method == "POST":
        form = UserCreationForm(request.POST)

        if form.is_valid():
            usuario = form.save()
            nombre_usuario = form.cleaned_data.get(
                'username')  # obtiene el nombre del usuario
            # crea un mensaje para el usuario
            messages.success(
                request, f"Nueva Cuenta Creada : {nombre_usuario}")
            login(request, usuario)
            messages.info(request, f"Has sido logueado como {nombre_usuario}")
            return redirect("main:homepage")
        else:
            for msg in form.error_messages:
                # print("ERROR:", msg)
                messages.error(request, f"{msg}: {form.error_messages[msg]}")

    return render(request, "main/registro.html", {"form": form})


def logout_request(request):
    logout(request)
    messages.info(request, "Saliste exitosamente")
    return redirect("main:homepage")


def login_request(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            usuario = form.cleaned_data.get('username')
            contraseña = form.cleaned_data.get('password')
            user = authenticate(username=usuario, password=contraseña)

            if user is not None:
                login(request, user)
                messages.info(request, f"Estas logueado como {usuario}")
                return redirect("main:homepage")
            else:
                messages.error(request, "Usuario o contraseña equivocada")
        else:
            messages.error(request, "Usuario o contraseña equivocada")

    form = AuthenticationForm()
    return render(request, "main/login.html", {"form": form})


def homepage(request):
    return HttpResponse('')

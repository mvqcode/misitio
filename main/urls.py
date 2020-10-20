from django.urls import path, include
from django.conf.urls import include, url
from django.contrib import admin
from . import views

app_name = 'main'

urlpatterns = [
    # path('', views.homepage, name='homepage'),
    path('', views.recomendados, name='homepage'),
    path('registro/', views.SignUpView.as_view(), name="registro"),
    path('registro1/', views.registro, name="registro1"),
    path('logout/', views.logout_request, name="logout"),
    path('login/', views.login_request, name="login"),
    path('busqueda/', views.busqueda, name="busqueda"),
    path('recomendados/', views.recomendados, name="redomendados"),
    path('check/', views.check, name="check"),
    path('user/', views.perfiluser, name="perfiluser"),
    path('login/recuperacion/', views.recuperacion, name="recuperacion"),
    path('login/usuariorec/', views.usuariorec, name="usuariorec"),
    path('categoria/<slug:nomcat>/', views.categoria,
         name="categoria"),  # Esto es URL dispatcher
]

admin.site.site_header = 'Panel de administración de Ultinoticias'

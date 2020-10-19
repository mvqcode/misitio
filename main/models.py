from django.db import models  # hereda del modelo base de django
from datetime import datetime
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
# Create your models here.


class Perfil(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    organizacion = models.TextField(max_length=30, default="Ninguna")
    email = models.EmailField(blank=False)

    def __str__(self):  # version imprimible
        return self.usuario.username


def crear_usuario_perfil(sender, instance, created, **kwargs):
    if created:
        Perfil.objects.create(usuario=instance)


def guardar_usuario_perfil(sender, instance, **kwargs):
    instance.pefil.save()


class Categoria(models.Model):
    categoria = models.CharField(max_length=20, primary_key=True)
    descripcion = models.TextField()


class Fuente(models.Model):
    diario = models.CharField(max_length=50)
    url = models.TextField(max_length=250)
    categoria = models.ForeignKey(
        Categoria, on_delete=models.CASCADE, null=True)
    activo = models.BooleanField(default=False)


class Noticia(models.Model):
    id_noticia = models.IntegerField(primary_key=True)
    titulo = models.TextField()
    descripcion = models.TextField()
    url = models.TextField()
    urlImagen = models.TextField()
    fecha = models.DateTimeField()
    autor = models.CharField(max_length=50)
    nombre = models.CharField(max_length=50)
    fuente = models.ForeignKey(Fuente, on_delete=models.CASCADE, null=True)


class Preferencia(models.Model):
    id_noticia = models.ForeignKey(
        Noticia, on_delete=models.CASCADE, null=True)
    usuario = models.CharField(max_length=50)
    preferencia = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id_noticia)


# el modelo se debe instalar en settings.py
# luego hacer las migraciones
# python manage.py makemigration
# python manage.py migrate

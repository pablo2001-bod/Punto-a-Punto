from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views
urlpatterns = [
    path('', views.inicio),
    #Clientes
    path("clientes/listadoCliente/", views.listadoCliente),
    path("clientes/nuevoCliente/", views.nuevoCliente),
    path("clientes/guardarCliente/", views.guardarCliente),
    #Oficinas
    path("oficinas/listadoOficina/", views.listadoOficina),
    path("oficinas/nuevaOficina/", views.nuevaOficina),
    path("oficinas/guardarOficina/", views.guardarOficina),
]
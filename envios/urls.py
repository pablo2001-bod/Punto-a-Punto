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
    #Transportes
    path("transportes/listadoTransporte/", views.listadoTransporte),
    path("transportes/nuevoTransporte/", views.nuevoTransporte),
    path("transportes/guardarTransporte/", views.guardarTransporte),
    #Seguros
    path("seguros/listadoSeguro/", views.listadoSeguro),
    path("seguros/nuevoSeguro/", views.nuevoSeguro),
    path("seguros/guardarSeguro/", views.guardarSeguro),
    #Encomiendas
    path("encomiendas/listadoEncomienda/", views.listadoEncomienda),
    path("encomiendas/nuevaEncomienda/", views.nuevaEncomienda),
    path("encomiendas/guardarEncomienda/", views.guardarEncomienda),
    path("encomiendas/detalleEncomienda/<id>/", views.detalleEncomienda),
    path("encomiendas/actualizarEstadoEncomienda/<id>/", views.actualizarEstadoEncomienda),
]
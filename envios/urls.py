from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    path('', views.inicio),
    
    # Clientes
    path("clientes/listadoCliente/", views.listadoCliente),
    path("clientes/nuevoCliente/", views.nuevoCliente),
    path("clientes/guardarCliente/", views.guardarCliente),
    path("clientes/editarCliente/<id>/", views.editarCliente),
    path("clientes/actualizarCliente/<id>/", views.actualizarCliente),
    path("clientes/eliminarCliente/<id>/", views.eliminarCliente),
    
    # Oficinas
    path("oficinas/listadoOficina/", views.listadoOficina),
    path("oficinas/nuevaOficina/", views.nuevaOficina),
    path("oficinas/guardarOficina/", views.guardarOficina),
    path("oficinas/editarOficina/<id>/", views.editarOficina),
    path("oficinas/actualizarOficina/<id>/", views.actualizarOficina),
    path("oficinas/eliminarOficina/<id>/", views.eliminarOficina),
    
    # Transportes
    path("transportes/listadoTransporte/", views.listadoTransporte),
    path("transportes/nuevoTransporte/", views.nuevoTransporte),
    path("transportes/guardarTransporte/", views.guardarTransporte),
    path("transportes/editarTransporte/<id>/", views.editarTransporte),
    path("transportes/actualizarTransporte/<id>/", views.actualizarTransporte),
    
    # Seguros
    path("seguros/listadoSeguro/", views.listadoSeguro),
    path("seguros/nuevoSeguro/", views.nuevoSeguro),
    path("seguros/guardarSeguro/", views.guardarSeguro),
    
    # Encomiendas
    path("encomiendas/listadoEncomienda/", views.listadoEncomienda),
    path("encomiendas/nuevaEncomienda/", views.nuevaEncomienda),
    path("encomiendas/guardarEncomienda/", views.guardarEncomienda),
    path("encomiendas/detalleEncomienda/<id>/", views.detalleEncomienda),
    path("encomiendas/actualizarEstadoEncomienda/<id>/", views.actualizarEstadoEncomienda),
    
    # Seguimiento
    path("seguimiento/seguimientoEncomienda/", views.seguimientoEncomienda),
    
    # REPORTES
    path("reportes/listadoReporte/", views.listadoReporte),
    path("reportes/nuevoReporte/<id>/", views.nuevoReporte),
    path("reportes/guardarReporte/", views.guardarReporte),
    
    # Notificaciones
    path("notificaciones/listadoNotificacion/", views.listadoNotificacion),
]
# urls.py
from django.urls import path
from envios import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    
    # Clientes
    path('clientes/listadoCliente/', views.listadoCliente, name='listadoCliente'),
    path('clientes/nuevoCliente/', views.nuevoCliente, name='nuevoCliente'),
    path('clientes/guardarCliente/', views.guardarCliente, name='guardarCliente'),  
    path('clientes/editarCliente/<int:id>/', views.editarCliente, name='editarCliente'),
    path('clientes/actualizarCliente/<int:id>/', views.actualizarCliente, name='actualizarCliente'),
    path('clientes/eliminarCliente/<int:id>/', views.eliminarCliente, name='eliminarCliente'),

    # Oficinas
    path('oficinas/listadoOficina/', views.listadoOficina, name='listadoOficina'),
    path('oficinas/nuevaOficina/', views.nuevaOficina, name='nuevaOficina'),
    path('oficinas/guardarOficina/', views.guardarOficina, name='guardarOficina'),
    path('oficinas/editarOficina/<int:id>/', views.editarOficina, name='editarOficina'),
    path('oficinas/actualizarOficina/<int:id>/', views.actualizarOficina, name='actualizarOficina'),
    path('oficinas/eliminarOficina/<int:id>/', views.eliminarOficina, name='eliminarOficina'),

    # Transportes
    path('transportes/listadoTransporte/', views.listadoTransporte, name='listadoTransporte'),
    path('transportes/nuevoTransporte/', views.nuevoTransporte, name='nuevoTransporte'),
    path('transportes/guardarTransporte/', views.guardarTransporte, name='guardarTransporte'),
    path('transportes/editarTransporte/<int:id>/', views.editarTransporte, name='editarTransporte'),
    path('transportes/actualizarTransporte/<int:id>/', views.actualizarTransporte, name='actualizarTransporte'),
    path('transportes/eliminarTransporte/<int:id>/', views.eliminarTransporte, name='eliminarTransporte'),

    # Seguros
    path('seguros/listadoSeguro/', views.listadoSeguro, name='listadoSeguro'),
    path('seguros/nuevoSeguro/', views.nuevoSeguro, name='nuevoSeguro'),
    path('seguros/guardarSeguro/', views.guardarSeguro, name='guardarSeguro'),

    # Encomiendas
    path('encomiendas/listadoEncomienda/', views.listadoEncomienda, name='listadoEncomienda'),
    path('encomiendas/nuevaEncomienda/', views.nuevaEncomienda, name='nuevaEncomienda'),
    path('encomiendas/guardarEncomienda/', views.guardarEncomienda, name='guardarEncomienda'),
    path('encomiendas/editarEncomienda/<int:id>/', views.editarEncomienda, name='editarEncomienda'),
    path('encomiendas/actualizarEncomienda/<int:id>/', views.actualizarEncomienda, name='actualizarEncomienda'),
    path('encomiendas/eliminarEncomienda/<int:id>/', views.eliminarEncomienda, name='eliminarEncomienda'),
    path('encomiendas/detalleEncomienda/<int:id>/', views.detalleEncomienda, name='detalleEncomienda'),
    path('encomiendas/actualizarEstadoEncomienda/<int:id>/', views.actualizarEstadoEncomienda, name='actualizarEstadoEncomienda'),

    # Seguimiento
    path('seguimiento/seguimientoEncomienda/', views.seguimientoEncomienda, name='seguimientoEncomienda'),

    # Reportes
    path('reportes/listadoReporte/', views.listadoReporte, name='listadoReporte'),
    path('reportes/nuevoReporte/<int:id>/', views.nuevoReporte, name='nuevoReporte'),
    path('reportes/guardarReporte/', views.guardarReporte, name='guardarReporte'),

    # Notificaciones
    path('notificaciones/listadoNotificacion/', views.listadoNotificacion, name='listadoNotificacion'),
]
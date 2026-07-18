from django.shortcuts import render, redirect
from envios.models import Cliente, Oficina, Transporte, Seguro, Encomienda, Reporte, NotificacionCorreo
from django.contrib import messages
import uuid
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

#Enviar Notificacion
def enviar_notificacion(encomienda, asunto, mensaje):
    correos = {
        encomienda.cliente.email,
        encomienda.email_destinatario,
    }

    for correo in correos:
        if not correo:
            continue

        cantidad_enviada = send_mail(
            asunto,
            mensaje,
            getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@puntoapunto.com"),
            [correo],
            fail_silently=True,
        )

        NotificacionCorreo.objects.create(
            encomienda=encomienda,
            destinatario=correo,
            asunto=asunto,
            mensaje=mensaje,
            enviado=cantidad_enviada > 0,
        )



def inicio(request):
    return render(request, 'inicio.html')

# Clientes
def listadoCliente(request):
    clientes = Cliente.objects.all().order_by("-id_cliente")
    return render(request, "clientes/listadoCliente.html", {"clientes": clientes})

def nuevoCliente(request):
    return render(request, "clientes/nuevoCliente.html")

def guardarCliente(request):
    if request.method == "POST":
        Cliente.objects.create(
            cedula=request.POST["cedula"],
            nombres=request.POST["nombres"],
            apellidos=request.POST["apellidos"],
            email=request.POST["email"],
            telefono=request.POST["telefono"],
            direccion=request.POST["direccion"],
        )
        messages.success(request, "Cliente registrado correctamente.")
    return redirect("/clientes/listadoCliente")

#Oficinas
def listadoOficina(request):
    oficinas = Oficina.objects.all().order_by("-id_oficina")
    return render(request, "oficinas/listadoOficina.html", {"oficinas": oficinas})

def nuevaOficina(request):
    return render(request, "oficinas/nuevaOficina.html")

def guardarOficina(request):
    if request.method == "POST":
        Oficina.objects.create(
            nombre=request.POST["nombre"],
            ciudad=request.POST["ciudad"],
            direccion=request.POST["direccion"],
            telefono=request.POST["telefono"],
            email=request.POST.get("email", ""),
        )
        messages.success(request, "Oficina registrada correctamente.")
    return redirect("/oficinas/listadoOficina")

#Trasportes
def listadoTransporte(request):
    transportes = Transporte.objects.all().order_by("-id_transporte")
    return render(
        request,
        "transportes/listadoTransporte.html",
        {"transportes": transportes},
    )

def nuevoTransporte(request):
    return render(
        request,
        "transportes/nuevoTransporte.html",
        {
            "tipos_transporte": Transporte.TIPOS_TRANSPORTE,
            "estados_transporte": Transporte.ESTADOS_TRANSPORTE,
        },
    )

def guardarTransporte(request):
    if request.method == "POST":
        Transporte.objects.create(
            placa=request.POST["placa"],
            tipo=request.POST["tipo"],
            marca=request.POST["marca"],
            modelo=request.POST["modelo"],
            capacidad_kg=request.POST["capacidad_kg"],
            estado=request.POST["estado"],
        )
        messages.success(request, "Transporte registrado correctamente.")
    return redirect("/transportes/listadoTransporte/")

#Seguros
def listadoSeguro(request):
    seguros = Seguro.objects.all().order_by("-id_seguro")
    return render(request, "seguros/listadoSeguro.html", {"seguros": seguros})

def nuevoSeguro(request):
    return render(request, "seguros/nuevoSeguro.html")

def guardarSeguro(request):
    if request.method == "POST":
        Seguro.objects.create(
            nombre=request.POST["nombre"],
            descripcion=request.POST["descripcion"],
            porcentaje_cobertura=request.POST["porcentaje_cobertura"],
            costo=request.POST["costo"],
            activo="activo" in request.POST,
        )
        messages.success(request, "Seguro registrado correctamente.")
    return redirect("/seguros/listadoSeguro/")

#Encomiendas
def listadoEncomienda(request):
    encomiendas = (
        Encomienda.objects.select_related(
            "cliente",
            "oficina_origen",
            "oficina_destino",
            "transporte",
            "seguro",
        )
        .all()
        .order_by("-id_encomienda")
    )
    return render(
        request,
        "encomiendas/listadoEncomienda.html",
        {"encomiendas": encomiendas},
    )

def nuevaEncomienda(request):
    datos = {
        "clientes": Cliente.objects.all().order_by("apellidos", "nombres"),
        "oficinas": Oficina.objects.all().order_by("ciudad", "nombre"),
        "transportes": Transporte.objects.filter(estado="DISPONIBLE").order_by("placa"),
        "seguros": Seguro.objects.filter(activo=True).order_by("nombre"),
    }
    return render(request, "encomiendas/nuevaEncomienda.html", datos)

def guardarEncomienda(request):
    if request.method == "POST":
        cliente = Cliente.objects.get(id_cliente=request.POST["cliente"])
        oficina_origen = Oficina.objects.get(
            id_oficina=request.POST["oficina_origen"]
        )
        oficina_destino = Oficina.objects.get(
            id_oficina=request.POST["oficina_destino"]
        )

        transporte = None
        if request.POST.get("transporte"):
            transporte = Transporte.objects.get(
                id_transporte=request.POST["transporte"]
            )

        seguro = None
        if request.POST.get("seguro"):
            seguro = Seguro.objects.get(id_seguro=request.POST["seguro"])

        encomienda = Encomienda.objects.create(
            codigo_seguimiento=f"ENC-{uuid.uuid4().hex[:8].upper()}",
            cliente=cliente,
            oficina_origen=oficina_origen,
            oficina_destino=oficina_destino,
            transporte=transporte,
            seguro=seguro,
            nombre_destinatario=request.POST["nombre_destinatario"],
            cedula_destinatario=request.POST["cedula_destinatario"],
            email_destinatario=request.POST["email_destinatario"],
            telefono_destinatario=request.POST["telefono_destinatario"],
            direccion_destino=request.POST["direccion_destino"],
            descripcion=request.POST["descripcion"],
            peso_kg=request.POST["peso_kg"],
            valor_declarado=request.POST.get("valor_declarado", 0),
            costo_envio=request.POST.get("costo_envio", 0),
        )

        asunto = f"Encomienda registrada: {encomienda.codigo_seguimiento}"
        mensaje_correo = (
            f"Su encomienda fue registrada correctamente.\n\n"
            f"Código de seguimiento: {encomienda.codigo_seguimiento}\n"
            f"Origen: {encomienda.oficina_origen}\n"
            f"Destino: {encomienda.oficina_destino}\n"
            f"Estado: {encomienda.get_estado_display()}\n"
        )
        enviar_notificacion(encomienda, asunto, mensaje_correo)
        messages.success(
            request,
            f"Encomienda registrada. Código: {encomienda.codigo_seguimiento}",
        )
        return redirect(f"/encomiendas/detalleEncomienda/{encomienda.id_encomienda}/")
    return redirect("/encomiendas/listadoEncomienda/")

def detalleEncomienda(request, id):
    encomienda = Encomienda.objects.select_related(
        "cliente",
        "oficina_origen",
        "oficina_destino",
        "transporte",
        "seguro",
    ).get(id_encomienda=id)
    reportes = encomienda.reportes.all().order_by("-fecha_reporte")
    return render(
        request,
        "encomiendas/detalleEncomienda.html",
        {
            "encomienda": encomienda,
            "reportes": reportes,
        },
    )

def actualizarEstadoEncomienda(request, id):
    encomienda = Encomienda.objects.get(id_encomienda=id)
    if request.method == "POST":
        encomienda.estado = request.POST["estado"]
        if encomienda.estado == "ENTREGADA":
            encomienda.fecha_entrega = timezone.now()
        encomienda.save()
        asunto = f"Actualización de encomienda {encomienda.codigo_seguimiento}"
        mensaje_correo = (
            f"El estado de su encomienda cambió.\n\n"
            f"Código: {encomienda.codigo_seguimiento}\n"
            f"Nuevo estado: {encomienda.get_estado_display()}\n"
        )
        enviar_notificacion(encomienda, asunto, mensaje_correo)
        messages.success(request, "Estado actualizado correctamente.")
        return redirect(f"/encomiendas/detalleEncomienda/{encomienda.id_encomienda}/")
    return render(
        request,
        "encomiendas/actualizarEstadoEncomienda.html",
        {
            "encomienda": encomienda,
            "estados_encomienda": Encomienda.ESTADOS_ENCOMIENDA,
        },
    )

# SEGUIMIENTO

def seguimientoEncomienda(request):
    encomienda = None
    busqueda_realizada = False

    if request.method == "POST":
        busqueda_realizada = True
        codigo = request.POST.get("codigo", "").strip()

        encomienda = Encomienda.objects.select_related(
            "oficina_origen",
            "oficina_destino",
        ).filter(codigo_seguimiento__iexact=codigo).first()

    return render(
        request,
        "seguimiento/seguimientoEncomienda.html",
        {
            "encomienda": encomienda,
            "busqueda_realizada": busqueda_realizada,
        },
    )

from django.shortcuts import render, redirect, get_object_or_404
from envios.models import Cliente, Oficina, Transporte, Seguro, Encomienda, Reporte, NotificacionCorreo
from django.contrib import messages
import uuid
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from envios.forms import ClienteForm, OficinaForm

# ==========================================
# FUNCIÓN AUXILIAR: Enviar Notificacion
# ==========================================
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

# ==========================================
# INICIO
# ==========================================
def inicio(request):
    return render(request, 'inicio.html')

# ==========================================
# MÓDULO: Clientes
# ==========================================
def listadoCliente(request):
    clientes = Cliente.objects.all().order_by("-id_cliente")
    return render(request, "clientes/listadoCliente.html", {"clientes": clientes})

def nuevoCliente(request):
    form = ClienteForm()
    return render(request, "clientes/nuevoCliente.html", {"form": form})

def guardarCliente(request):
    if request.method == "POST":
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Cliente registrado correctamente.")
            # Cambiar esto:
            # return redirect("/clientes/listadoCliente")
            
            # Por esto:
            return redirect("listadoCliente") 
        else:
            return render(request, "clientes/nuevoCliente.html", {"form": form})
    return redirect("listadoCliente")

def editarCliente(request, id):
    cliente = get_object_or_404(Cliente, id_cliente=id)
    form = ClienteForm(instance=cliente)
    return render(request, "clientes/editarCliente.html", {"form": form, "cliente": cliente})


def actualizarCliente(request, id):
    cliente = get_object_or_404(Cliente, id_cliente=id)
    if request.method == "POST":
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            messages.success(request, "Cliente actualizado correctamente.")
            return redirect("listadoCliente") # <-- Usa el name de la URL
        else:
            return render(request, "clientes/editarCliente.html", {"form": form, "cliente": cliente})
    return redirect("listadoCliente")

def eliminarCliente(request, id):
    cliente = get_object_or_404(Cliente, id_cliente=id)
    cliente.delete()
    messages.success(request, "Cliente eliminado correctamente.")
    return redirect("/clientes/listadoCliente")

# ==========================================
# MÓDULO: Oficinas
# ==========================================
def listadoOficina(request):
    oficinas = Oficina.objects.all().order_by("-id_oficina")
    return render(request, "oficinas/listadoOficina.html", {"oficinas": oficinas})

def nuevaOficina(request):
    form = OficinaForm()
    return render(request, "oficinas/nuevaOficina.html", {"form": form})

def guardarOficina(request):
    if request.method == "POST":
        form = OficinaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Oficina registrada correctamente.")
            return redirect("/oficinas/listadoOficina")
        else:
            return render(request, "oficinas/nuevaOficina.html", {"form": form})
    return redirect("/oficinas/listadoOficina")

def editarOficina(request, id):
    oficina = get_object_or_404(Oficina, id_oficina=id)
    return render(request, "oficinas/editarOficina.html", {"oficina": oficina})

def actualizarOficina(request, id):
    oficina = get_object_or_404(Oficina, id_oficina=id)
    if request.method == "POST":
        oficina.nombre = request.POST["nombre"]
        oficina.ciudad = request.POST["ciudad"]
        oficina.direccion = request.POST["direccion"]
        oficina.telefono = request.POST["telefono"]
        oficina.email = request.POST.get("email", "")
        oficina.save()
        messages.success(request, "Oficina actualizada correctamente.")
        return redirect("/oficinas/listadoOficina/")
    return redirect("/oficinas/listadoOficina/")

def eliminarOficina(request, id):
    oficina = get_object_or_404(Oficina, id_oficina=id)
    oficina.delete()
    messages.success(request, "Oficina eliminada correctamente.")
    return redirect("/oficinas/listadoOficina/")

# ==========================================
# MÓDULO: TRANSPORTES
# ==========================================
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
#GUARDAR
def guardarTransporte(request):
    if request.method == "POST":
        # Se agregan validaciones básicas antes de crear
        placa = request.POST.get("placa", "").strip().upper()
        
        # Validación de placa única
        if Transporte.objects.filter(placa=placa).exists():
            messages.error(request, f"La placa {placa} ya está registrada.")
            return redirect("/transportes/nuevoTransporte/")

        try:
            Transporte.objects.create(
                placa=placa,
                tipo=request.POST["tipo"],
                marca=request.POST["marca"],
                modelo=request.POST["modelo"],
                capacidad_kg=request.POST["capacidad_kg"],
                estado=request.POST["estado"],
            )
            messages.success(request, "Transporte registrado correctamente.")
        except Exception as e:
            messages.error(request, f"Error al registrar: {e}")
            return redirect("/transportes/nuevoTransporte/")
            
    return redirect("/transportes/listadoTransporte/")
#EDITAR
def editarTransporte(request, id):
    transporte = get_object_or_404(Transporte, id_transporte=id)
    return render(
        request,
        "transportes/editarTransporte.html",
        {
            "transporte": transporte,
            "tipos_transporte": Transporte.TIPOS_TRANSPORTE,
            "estados_transporte": Transporte.ESTADOS_TRANSPORTE,
        },
    )

def actualizarTransporte(request, id):
    transporte = get_object_or_404(Transporte, id_transporte=id)
    if request.method == "POST":
        placa = request.POST.get("placa", "").strip().upper()

        # Validación de placa única (excluyendo el transporte actual)
        if Transporte.objects.filter(placa=placa).exclude(id_transporte=id).exists():
            messages.error(request, f"La placa {placa} ya está registrada en otro vehículo.")
            return redirect(f"/transportes/editarTransporte/{id}/")

        try:
            transporte.placa = placa
            transporte.tipo = request.POST["tipo"]
            transporte.marca = request.POST["marca"]
            transporte.modelo = request.POST["modelo"]
            transporte.capacidad_kg = request.POST["capacidad_kg"]
            transporte.estado = request.POST["estado"]
            transporte.save()
            messages.success(request, "Transporte actualizado correctamente.")
        except Exception as e:
            messages.error(request, f"Error al actualizar: {e}")
            return redirect(f"/transportes/editarTransporte/{id}/")
            
        return redirect("/transportes/listadoTransporte/")
    return redirect("/transportes/listadoTransporte/")

#ELIMINAR

def eliminarTransporte(request, id):
    transporte = get_object_or_404(Transporte, id_transporte=id)
    placa = transporte.placa
    
    try:
        
        transporte.encomiendas.update(transporte=None)
        
        # Ahora sí lo eliminamos físicamente de la base de datos
        transporte.delete()
        messages.success(request, f"Transporte con placa {placa} eliminado correctamente.")
    except Exception as e:
        messages.error(request, f"No se pudo eliminar el transporte: {e}")
        
    return redirect("/transportes/listadoTransporte/")

# ==========================================
# MÓDULO: Seguros
# ==========================================
def listadoSeguro(request):
    seguros = Seguro.objects.all().order_by("-id_seguro")
    return render(request, "seguros/listadoSeguro.html", {"seguros": seguros})

def nuevoSeguro(request):
    return render(request, "seguros/nuevoSeguro.html")

def guardarSeguro(request):
    if request.method == "POST":
        try:
            Seguro.objects.create(
                nombre=request.POST["nombre"],
                descripcion=request.POST["descripcion"],
                porcentaje_cobertura=request.POST["porcentaje_cobertura"],
                costo=request.POST["costo"],
                activo="activo" in request.POST,
            )
            messages.success(request, "Seguro registrado correctamente.")
        except Exception as e:
            messages.error(request, f"Error al registrar seguro: {e}")
            
    return redirect("/seguros/listadoSeguro/")

# ==========================================
# MÓDULO: Encomiendas
# ==========================================
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
        try:
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

            # Notificación por correo
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
            
        except Exception as e:
            messages.error(request, f"Error al registrar encomienda: {e}")
            return redirect("/encomiendas/nuevaEncomienda/")
            
    return redirect("/encomiendas/listadoEncomienda/")

def editarEncomienda(request, id):
    encomienda = get_object_or_404(Encomienda, id_encomienda=id)
    datos = {
        "encomienda": encomienda,
        "clientes": Cliente.objects.all().order_by("apellidos", "nombres"),
        "oficinas": Oficina.objects.all().order_by("ciudad", "nombre"),
        "transportes": Transporte.objects.all().order_by("placa"),
        "seguros": Seguro.objects.filter(activo=True).order_by("nombre"),
    }
    return render(request, "encomiendas/editarEncomienda.html", datos)

def actualizarEncomienda(request, id):
    encomienda = get_object_or_404(Encomienda, id_encomienda=id)
    if request.method == "POST":
        try:
            encomienda.cliente = Cliente.objects.get(id_cliente=request.POST["cliente"])
            encomienda.oficina_origen = Oficina.objects.get(id_oficina=request.POST["oficina_origen"])
            encomienda.oficina_destino = Oficina.objects.get(id_oficina=request.POST["oficina_destino"])

            transporte = None
            if request.POST.get("transporte"):
                transporte = Transporte.objects.get(id_transporte=request.POST["transporte"])
            encomienda.transporte = transporte

            seguro = None
            if request.POST.get("seguro"):
                seguro = Seguro.objects.get(id_seguro=request.POST["seguro"])
            encomienda.seguro = seguro

            encomienda.nombre_destinatario = request.POST["nombre_destinatario"]
            encomienda.cedula_destinatario = request.POST["cedula_destinatario"]
            encomienda.email_destinatario = request.POST["email_destinatario"]
            encomienda.telefono_destinatario = request.POST["telefono_destinatario"]
            encomienda.direccion_destino = request.POST["direccion_destino"]
            encomienda.descripcion = request.POST["descripcion"]
            encomienda.peso_kg = request.POST["peso_kg"]
            encomienda.valor_declarado = request.POST.get("valor_declarado", 0)
            encomienda.costo_envio = request.POST.get("costo_envio", 0)
            encomienda.save()
            
            messages.success(request, "Encomienda actualizada correctamente.")
            return redirect(f"/encomiendas/detalleEncomienda/{encomienda.id_encomienda}/")
        except Exception as e:
            messages.error(request, f"Error al actualizar encomienda: {e}")
            return redirect(f"/encomiendas/editarEncomienda/{id}/")
            
    return redirect("/encomiendas/listadoEncomienda/")

def eliminarEncomienda(request, id):
    encomienda = get_object_or_404(Encomienda, id_encomienda=id)
    codigo = encomienda.codigo_seguimiento
    encomienda.delete()
    messages.success(request, f"Encomienda {codigo} eliminada correctamente.")
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
        try:
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
        except Exception as e:
            messages.error(request, f"Error al actualizar estado: {e}")
            
        return redirect(f"/encomiendas/detalleEncomienda/{encomienda.id_encomienda}/")
        
    return render(
        request,
        "encomiendas/actualizarEstadoEncomienda.html",
        {
            "encomienda": encomienda,
            "estados_encomienda": Encomienda.ESTADOS_ENCOMIENDA,
        },
    )

# ==========================================
# MÓDULO: SEGUIMIENTO
# ==========================================
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

# ==========================================
# MÓDULO: REPORTES
# ==========================================
def listadoReporte(request):
    reportes = Reporte.objects.select_related("encomienda").all().order_by(
        "-fecha_reporte"
    )
    return render(request, "reportes/listadoReporte.html", {"reportes": reportes})

def nuevoReporte(request, id):
    encomienda = Encomienda.objects.get(id_encomienda=id)
    return render(
        request,
        "reportes/nuevoReporte.html",
        {
            "encomienda": encomienda,
            "tipos_reporte": Reporte.TIPOS_REPORTE,
        },
    )

def guardarReporte(request):
    if request.method == "POST":
        try:
            encomienda = Encomienda.objects.get(
                id_encomienda=request.POST["encomienda"]
            )

            reporte = Reporte.objects.create(
                encomienda=encomienda,
                tipo=request.POST["tipo"],
                detalle=request.POST["detalle"],
                resuelto="resuelto" in request.POST,
            )

            asunto = f"Novedad de encomienda {encomienda.codigo_seguimiento}"
            mensaje_correo = (
                f"Se registró una novedad en su encomienda.\n\n"
                f"Tipo: {reporte.get_tipo_display()}\n"
                f"Detalle: {reporte.detalle}\n"
            )
            enviar_notificacion(encomienda, asunto, mensaje_correo)

            messages.success(request, "Reporte registrado correctamente.")
            return redirect(f"/encomiendas/detalleEncomienda/{encomienda.id_encomienda}/")
        except Exception as e:
            messages.error(request, f"Error al guardar reporte: {e}")
            
    return redirect("reportes/listadoReporte")
def editarReporte(request, id):
    reporte = get_object_or_404(Reporte, id_reporte=id)
    return render(
        request,
        "reportes/editarReporte.html",
        {
            "reporte": reporte,
            "tipos_reporte": Reporte.TIPOS_REPORTE,
        }
    )

def actualizarReporte(request, id):
    reporte = get_object_or_404(Reporte, id_reporte=id)
    if request.method == "POST":
        reporte.tipo = request.POST["tipo"]
        reporte.detalle = request.POST["detalle"]
        reporte.resuelto = "resuelto" in request.POST
        reporte.save()
        messages.success(request, "Reporte actualizado correctamente.")
        return redirect("/reportes/listadoReporte/")
    return redirect("/reportes/listadoReporte/")

def eliminarReporte(request, id):
    reporte = get_object_or_404(Reporte, id_reporte=id)
    reporte.delete()
    messages.success(request, "Reporte eliminado correctamente.")
    return redirect("/reportes/listadoReporte/")

def resolverReporte(request, id):
    reporte = get_object_or_404(Reporte, id_reporte=id)
    reporte.resuelto = True
    reporte.save()
    messages.success(request, "El reporte ha sido marcado como resuelto.")
    return redirect("/reportes/listadoReporte/")

# ==========================================
# MÓDULO: Notificaciones
# ==========================================
def listadoNotificacion(request):
    notificaciones = (
        NotificacionCorreo.objects.select_related("encomienda")
        .all()
        .order_by("-fecha_envio")
    )
    return render(
        request,
        "notificaciones/listadoNotificacion.html",
        {"notificaciones": notificaciones},
    )
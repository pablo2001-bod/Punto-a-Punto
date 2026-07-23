from django.shortcuts import render, redirect, get_object_or_404
from envios.models import Cliente, Oficina, Transporte, Seguro, Encomienda, Reporte, NotificacionCorreo
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail
import logging
import uuid
from django.utils import timezone
from envios.forms import ClienteForm, OficinaForm
from django.db.models import Sum
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test

#Importando lo nuevo:
import json
from django.db.models import Count, Sum

logger = logging.getLogger(__name__)


def es_administrador(user):
    return user.is_authenticated and user.is_superuser


def enviar_notificacion(encomienda, asunto, mensaje):
    """Envía el aviso al remitente y al destinatario sin interrumpir el flujo principal."""
    correos = {
        (encomienda.cliente.email or "").strip(),
        (encomienda.email_destinatario or "").strip(),
    }
    remitente = (
        getattr(settings, "DEFAULT_FROM_EMAIL", "")
        or getattr(settings, "EMAIL_HOST_USER", "")
        or "no-reply@puntoapunto.com"
    )

    for correo in correos:
        if not correo:
            continue

        enviado = False
        error_envio = ""

        try:
            cantidad_enviada = send_mail(
                subject=asunto,
                message=mensaje,
                from_email=remitente,
                recipient_list=[correo],
                fail_silently=False,
            )
            enviado = cantidad_enviada > 0
        except Exception as error:
            error_envio = str(error)
            logger.exception(
                "No se pudo enviar la notificación de la encomienda %s a %s",
                encomienda.codigo_seguimiento,
                correo,
            )

        try:
            mensaje_registro = mensaje
            if error_envio:
                mensaje_registro += f"\n\nError de envío: {error_envio}"

            NotificacionCorreo.objects.create(
                encomienda=encomienda,
                destinatario=correo,
                asunto=asunto,
                mensaje=mensaje_registro,
                enviado=enviado,
            )
        except Exception:
            logger.exception(
                "No se pudo registrar la notificación de la encomienda %s",
                encomienda.codigo_seguimiento,
            )


# ==========================================
# MÓDULO: AUTENTICACIÓN Y REGISTRO
# ==========================================
@login_required(login_url="/login/")
def inicio(request):
    return render(request, 'inicio.html')

def logout_view(request):
    logout(request)
    messages.success(request, "Has cerrado sesión correctamente.")
    return redirect("login")

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Bienvenido, {user.username}")
            return redirect("inicio")
        else:
            messages.error(request, "Usuario o contraseña incorrectos.")
    return render(request, "auth/login.html")

def registro_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")
        
        nombres = request.POST.get("nombres")
        apellidos = request.POST.get("apellidos")
        cedula = request.POST.get("cedula")
        telefono = request.POST.get("telefono")
        direccion = request.POST.get("direccion")

        if password1 != password2:
            messages.error(request, "Las contraseñas no coinciden.")
            return render(request, "auth/registro.html")

        if User.objects.filter(username=username).exists():
            messages.error(request, "El nombre de usuario ya está en uso.")
            return render(request, "auth/registro.html")

        if Cliente.objects.filter(cedula=cedula).exists():
            messages.error(request, "Ya existe un cliente registrado con esa cédula.")
            return render(request, "auth/registro.html")

        try:
            user = User.objects.create_user(username=username, email=email, password=password1)
            user.save()

            Cliente.objects.create(
                user=user,
                nombres=nombres,
                apellidos=apellidos,
                cedula=cedula,
                telefono=telefono,
                email=email,
                direccion=direccion
            )

            messages.success(request, "Cuenta creada exitosamente. Inicia sesión.")
            return redirect("login")
        except Exception as e:
            messages.error(request, f"Error al registrar: {e}")
            
    return render(request, "auth/registro.html")

# ==========================================
# MÓDULO: SEGUIMIENTO (SEPARADO ADMIN Y CLIENTE)
# ==========================================
@login_required(login_url="/login/")
def seguimientoEncomienda(request):
    if not request.user.is_superuser:
        return redirect('seguimientoCliente')
        
    encomienda_unica = None
    busqueda_realizada = False

    if request.method == "POST":
        busqueda_realizada = True
        codigo = request.POST.get("codigo", "").strip()
        encomienda_unica = Encomienda.objects.select_related(
            "oficina_origen", "oficina_destino"
        ).filter(codigo_seguimiento__iexact=codigo).first()
    
    return render(request, "seguimiento/seguimientoEncomienda.html", {
        "encomienda": encomienda_unica,
        "busqueda_realizada": busqueda_realizada
    })

@login_required(login_url="/login/")
def seguimientoClienteView(request):
    if request.user.is_superuser:
        return redirect('seguimientoEncomienda')

    try:
        cliente_actual = Cliente.objects.get(user=request.user)
        encomiendas = Encomienda.objects.select_related(
            "oficina_origen", "oficina_destino", "transporte"
        ).filter(cliente=cliente_actual).order_by("-fecha_registro")
    except Cliente.DoesNotExist:
        encomiendas = []

    return render(request, "seguimiento/seguimientoCliente.html", {
        "encomiendas": encomiendas
    })

# ==========================================
# MÓDULO: Clientes (Solo Admin)
# ==========================================
@user_passes_test(es_administrador, login_url="/seguimiento/seguimientoEncomienda/")
def listadoCliente(request):
    clientes = Cliente.objects.all().order_by("-id_cliente")
    return render(request, "clientes/listadoCliente.html", {"clientes": clientes})

@user_passes_test(es_administrador, login_url="/seguimiento/seguimientoEncomienda/")
def nuevoCliente(request):
    form = ClienteForm()
    return render(request, "clientes/nuevoCliente.html", {"form": form})

@user_passes_test(es_administrador, login_url="/seguimiento/seguimientoEncomienda/")
def guardarCliente(request):
    if request.method == "POST":
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Cliente registrado correctamente.")
            return redirect("/clientes/listadoCliente/")
        else:
            messages.error(request, f"Error al guardar: {form.errors}")
            return render(request, "clientes/nuevoCliente.html", {"form": form})
    return redirect("/clientes/listadoCliente/")

@user_passes_test(es_administrador, login_url="/seguimiento/seguimientoEncomienda/")
def editarCliente(request, id):
    cliente = get_object_or_404(Cliente, id_cliente=id)
    form = ClienteForm(instance=cliente)
    return render(request, "clientes/editarCliente.html", {"form": form, "cliente": cliente})

@user_passes_test(es_administrador, login_url="/seguimiento/seguimientoEncomienda/")
def actualizarCliente(request, id):
    cliente = get_object_or_404(Cliente, id_cliente=id)
    if request.method == "POST":
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            messages.success(request, "Cliente actualizado correctamente.")
            return redirect("listadoCliente")
        else:
            return render(request, "clientes/editarCliente.html", {"form": form, "cliente": cliente})
    return redirect("listadoCliente")

@user_passes_test(es_administrador, login_url="/seguimiento/seguimientoEncomienda/")
def eliminarCliente(request, id):
    cliente = get_object_or_404(Cliente, id_cliente=id)
    cliente.delete()
    messages.success(request, "Cliente eliminado correctamente.")
    return redirect("/clientes/listadoCliente")

# ==========================================
# MÓDULO: Oficinas (Solo Admin)
# ==========================================
@user_passes_test(es_administrador, login_url="/seguimiento/seguimientoEncomienda/")
def listadoOficina(request):
    oficinas = Oficina.objects.all().order_by("-id_oficina")
    return render(request, "oficinas/listadoOficina.html", {"oficinas": oficinas})

@user_passes_test(es_administrador, login_url="/seguimiento/seguimientoEncomienda/")
def nuevaOficina(request):
    form = OficinaForm()
    return render(request, "oficinas/nuevaOficina.html", {"form": form})

@user_passes_test(es_administrador, login_url="/seguimiento/seguimientoEncomienda/")
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

@user_passes_test(es_administrador, login_url="/seguimiento/seguimientoEncomienda/")
def editarOficina(request, id):
    oficina = get_object_or_404(Oficina, id_oficina=id)
    return render(request, "oficinas/editarOficina.html", {"oficina": oficina})

@user_passes_test(es_administrador, login_url="/seguimiento/seguimientoEncomienda/")
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

@user_passes_test(es_administrador, login_url="/seguimiento/seguimientoEncomienda/")
def eliminarOficina(request, id):
    oficina = get_object_or_404(Oficina, id_oficina=id)
    oficina.delete()
    messages.success(request, "Oficina eliminada correctamente.")
    return redirect("/oficinas/listadoOficina/")

# ==========================================
# MÓDULO: TRANSPORTES (Solo Admin)
# ==========================================
@user_passes_test(es_administrador, login_url="/seguimiento/seguimientoEncomienda/")
def listadoTransporte(request):
    transportes = Transporte.objects.all().order_by("-id_transporte")
    return render(request, "transportes/listadoTransporte.html", {"transportes": transportes})

@user_passes_test(es_administrador, login_url="/seguimiento/seguimientoEncomienda/")
def nuevoTransporte(request):
    return render(
        request,
        "transportes/nuevoTransporte.html",
        {
            "tipos_transporte": Transporte.TIPOS_TRANSPORTE,
            "estados_transporte": Transporte.ESTADOS_TRANSPORTE,
        },
    )

@user_passes_test(es_administrador, login_url="/seguimiento/seguimientoEncomienda/")
def guardarTransporte(request):
    if request.method == "POST":
        placa = request.POST.get("placa", "").strip().upper()
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

@user_passes_test(es_administrador, login_url="/seguimiento/seguimientoEncomienda/")
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

@user_passes_test(es_administrador, login_url="/seguimiento/seguimientoEncomienda/")
def actualizarTransporte(request, id):
    transporte = get_object_or_404(Transporte, id_transporte=id)
    if request.method == "POST":
        placa = request.POST.get("placa", "").strip().upper()
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

@user_passes_test(es_administrador, login_url="/seguimiento/seguimientoEncomienda/")
def eliminarTransporte(request, id):
    transporte = get_object_or_404(Transporte, id_transporte=id)
    placa = transporte.placa
    try:
        transporte.encomiendas.update(transporte=None)
        transporte.delete()
        messages.success(request, f"Transporte con placa {placa} eliminado correctamente.")
    except Exception as e:
        messages.error(request, f"No se pudo eliminar el transporte: {e}")
    return redirect("/transportes/listadoTransporte/")

# ==========================================
# MÓDULO: Seguros (Solo Admin) - CORREGIDO
# ==========================================
@user_passes_test(es_administrador, login_url="/seguimiento/seguimientoEncomienda/")
def listadoSeguro(request):
    seguros = Seguro.objects.all().order_by("-id_seguro")
    return render(request, "seguros/listadoSeguro.html", {"seguros": seguros})

@user_passes_test(es_administrador, login_url="/seguimiento/seguimientoEncomienda/")
def nuevoSeguro(request):
    return render(request, "seguros/nuevoSeguro.html")

@user_passes_test(es_administrador, login_url="/seguimiento/seguimientoEncomienda/")
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

@user_passes_test(es_administrador, login_url="/seguimiento/seguimientoEncomienda/")
def editarSeguro(request, id):
    seguro = get_object_or_404(Seguro, id_seguro=id) 
    return render(request, 'seguros/editarSeguro.html', {'seguro': seguro})

@user_passes_test(es_administrador, login_url="/seguimiento/seguimientoEncomienda/")
def actualizarSeguro(request, id):
    if request.method == 'POST':
        seguro = get_object_or_404(Seguro, id_seguro=id)
        seguro.nombre = request.POST.get('nombre')
        seguro.porcentaje_cobertura = request.POST.get('porcentaje_cobertura')
        seguro.costo = request.POST.get('costo')
        seguro.descripcion = request.POST.get('descripcion')
        seguro.activo = True if request.POST.get('activo') else False
        seguro.save()
        messages.success(request, 'El seguro ha sido actualizado correctamente.')
    return redirect('/seguros/listadoSeguro/')

@user_passes_test(es_administrador, login_url="/seguimiento/seguimientoEncomienda/")
def eliminarSeguro(request, id):
    seguro = get_object_or_404(Seguro, id_seguro=id) 
    seguro.delete()
    messages.success(request, 'El seguro ha sido eliminado correctamente.')
    return redirect('/seguros/listadoSeguro/')

# ==========================================
# MÓDULO: Encomiendas (Solo Admin)
# ==========================================
@user_passes_test(es_administrador, login_url="/seguimiento/seguimientoEncomienda/")
def listadoEncomienda(request):
    encomiendas = Encomienda.objects.select_related(
        "cliente", "oficina_origen", "oficina_destino", "transporte", "seguro"
    ).all().order_by("-id_encomienda")
    return render(request, "encomiendas/listadoEncomienda.html", {"encomiendas": encomiendas})

@user_passes_test(es_administrador, login_url="/seguimiento/seguimientoEncomienda/")
def nuevaEncomienda(request):
    datos = {
        "clientes": Cliente.objects.all().order_by("apellidos", "nombres"),
        "oficinas": Oficina.objects.all().order_by("ciudad", "nombre"),
        "transportes": Transporte.objects.filter(estado="DISPONIBLE").order_by("placa"),
        "seguros": Seguro.objects.filter(activo=True).order_by("nombre"),
    }
    return render(request, "encomiendas/nuevaEncomienda.html", datos)

@user_passes_test(es_administrador, login_url="/seguimiento/seguimientoEncomienda/")
def guardarEncomienda(request):
    if request.method == "POST":
        try:
            cliente = Cliente.objects.get(id_cliente=request.POST["cliente"])
            oficina_origen = Oficina.objects.get(id_oficina=request.POST["oficina_origen"])
            oficina_destino = Oficina.objects.get(id_oficina=request.POST["oficina_destino"])
            transporte = Transporte.objects.get(id_transporte=request.POST["transporte"]) if request.POST.get("transporte") else None
            seguro = Seguro.objects.get(id_seguro=request.POST["seguro"]) if request.POST.get("seguro") else None

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
                "Su encomienda fue registrada correctamente.\n\n"
                f"Código de seguimiento: {encomienda.codigo_seguimiento}\n"
                f"Origen: {encomienda.oficina_origen}\n"
                f"Destino: {encomienda.oficina_destino}\n"
                f"Estado: {encomienda.get_estado_display()}\n"
            )
            enviar_notificacion(encomienda, asunto, mensaje_correo)

            messages.success(request, f"Encomienda registrada. Código: {encomienda.codigo_seguimiento}")
            return redirect(f"/encomiendas/detalleEncomienda/{encomienda.id_encomienda}/")
        except Exception as e:
            messages.error(request, f"Error al registrar encomienda: {e}")
            return redirect("/encomiendas/nuevaEncomienda/")
    return redirect("/encomiendas/listadoEncomienda/")

@user_passes_test(es_administrador, login_url="/seguimiento/seguimientoEncomienda/")
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

@user_passes_test(es_administrador, login_url="/seguimiento/seguimientoEncomienda/")
def actualizarEncomienda(request, id):
    encomienda = get_object_or_404(Encomienda, id_encomienda=id)
    if request.method == "POST":
        try:
            encomienda.cliente = Cliente.objects.get(id_cliente=request.POST["cliente"])
            encomienda.oficina_origen = Oficina.objects.get(id_oficina=request.POST["oficina_origen"])
            encomienda.oficina_destino = Oficina.objects.get(id_oficina=request.POST["oficina_destino"])
            encomienda.transporte = Transporte.objects.get(id_transporte=request.POST["transporte"]) if request.POST.get("transporte") else None
            encomienda.seguro = Seguro.objects.get(id_seguro=request.POST["seguro"]) if request.POST.get("seguro") else None
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

@user_passes_test(es_administrador, login_url="/seguimiento/seguimientoEncomienda/")
def eliminarEncomienda(request, id):
    encomienda = get_object_or_404(Encomienda, id_encomienda=id)
    encomienda.delete()
    messages.success(request, "Encomienda eliminada correctamente.")
    return redirect("/encomiendas/listadoEncomienda/")

@user_passes_test(es_administrador, login_url="/seguimiento/seguimientoEncomienda/")
def detalleEncomienda(request, id):
    encomienda = get_object_or_404(Encomienda, id_encomienda=id)
    reportes = encomienda.reportes.all().order_by("-fecha_reporte")
    return render(request, "encomiendas/detalleEncomienda.html", {"encomienda": encomienda, "reportes": reportes})

@user_passes_test(es_administrador, login_url="/seguimiento/seguimientoEncomienda/")
def actualizarEstadoEncomienda(request, id):
    encomienda = get_object_or_404(Encomienda, id_encomienda=id)
    if request.method == "POST":
        try:
            encomienda.estado = request.POST["estado"]
            if encomienda.estado == "ENTREGADA":
                encomienda.fecha_entrega = timezone.now()
            encomienda.save()

            asunto = f"Actualización de encomienda {encomienda.codigo_seguimiento}"
            mensaje_correo = (
                "El estado de su encomienda cambió.\n\n"
                f"Código: {encomienda.codigo_seguimiento}\n"
                f"Nuevo estado: {encomienda.get_estado_display()}\n"
            )
            enviar_notificacion(encomienda, asunto, mensaje_correo)

            messages.success(request, "Estado actualizado correctamente.")
        except Exception as e:
            messages.error(request, f"Error al actualizar estado: {e}")
        return redirect(f"/encomiendas/detalleEncomienda/{encomienda.id_encomienda}/")
    return render(request, "encomiendas/actualizarEstadoEncomienda.html", {"encomienda": encomienda, "estados_encomienda": Encomienda.ESTADOS_ENCOMIENDA})

# ==========================================
# MÓDULO: REPORTES Y NOVEDADES (Solo Admin)
# ==========================================
@user_passes_test(es_administrador, login_url="/seguimiento/seguimientoEncomienda/")
def listadoReporte(request):
    reportes = Reporte.objects.select_related("encomienda").all().order_by("-fecha_reporte")
    return render(request, "reportes/listadoReporte.html", {"reportes": reportes})

@user_passes_test(es_administrador, login_url="/seguimiento/seguimientoEncomienda/")
def nuevoReporte(request, id):
    encomienda = get_object_or_404(Encomienda, id_encomienda=id)
    return render(request, "reportes/nuevoReporte.html", {"encomienda": encomienda, "tipos_reporte": Reporte.TIPOS_REPORTE})

@user_passes_test(es_administrador, login_url="/seguimiento/seguimientoEncomienda/")
def guardarReporte(request):
    if request.method == "POST":
        try:
            encomienda = Encomienda.objects.get(id_encomienda=request.POST["encomienda_id"])
            reporte = Reporte.objects.create(
                encomienda=encomienda,
                tipo=request.POST["tipo"],
                detalle=request.POST["detalle"]
            )

            asunto = f"Novedad de encomienda {encomienda.codigo_seguimiento}"
            mensaje_correo = (
                "Se registró una novedad en su encomienda.\n\n"
                f"Código: {encomienda.codigo_seguimiento}\n"
                f"Tipo: {reporte.get_tipo_display()}\n"
                f"Detalle: {reporte.detalle}\n"
            )
            enviar_notificacion(encomienda, asunto, mensaje_correo)

            messages.success(request, "Reporte registrado correctamente.")
            return redirect(f"/encomiendas/detalleEncomienda/{encomienda.id_encomienda}/")
        except Exception as e:
            messages.error(request, f"Error al guardar reporte: {e}")
    return redirect("/reportes/listadoReporte/")

@user_passes_test(es_administrador, login_url="/seguimiento/seguimientoEncomienda/")
def editarReporte(request, id):
    reporte = get_object_or_404(Reporte, id_reporte=id)
    return render(request, "reportes/editarReporte.html", {"reporte": reporte, "tipos_reporte": Reporte.TIPOS_REPORTE})

@user_passes_test(es_administrador, login_url="/seguimiento/seguimientoEncomienda/")
def actualizarReporte(request, id):
    reporte = get_object_or_404(Reporte, id_reporte=id)
    if request.method == "POST":
        try:
            reporte.tipo = request.POST["tipo"]
            reporte.detalle = request.POST["detalle"]
            reporte.save()
            messages.success(request, "Reporte actualizado correctamente.")
        except Exception as e:
            messages.error(request, f"Error al actualizar reporte: {e}")
    return redirect("/reportes/listadoReporte/")

@user_passes_test(es_administrador, login_url="/seguimiento/seguimientoEncomienda/")
def eliminarReporte(request, id):
    reporte = get_object_or_404(Reporte, id_reporte=id)
    encomienda_id = reporte.encomienda.id_encomienda
    reporte.delete()
    messages.success(request, "Reporte eliminado correctamente.")
    return redirect(f"/encomiendas/detalleEncomienda/{encomienda_id}/")

@user_passes_test(es_administrador, login_url="/seguimiento/seguimientoEncomienda/")
def resolverReporte(request, id):
    reporte = get_object_or_404(Reporte, id_reporte=id)
    reporte.resuelto = True
    reporte.save()
    messages.success(request, "Reporte marcado como resuelto.")
    return redirect("/reportes/listadoReporte/")

@user_passes_test(es_administrador, login_url="/seguimiento/seguimientoEncomienda/")
def reportesGenerales(request):
    # Obtener parámetros de filtro desde la petición GET
    fecha_inicio = request.GET.get("fecha_inicio")
    fecha_fin = request.GET.get("fecha_fin")
    estado = request.GET.get("estado")
    oficina = request.GET.get("oficina")

    # QuerySet base optimizado
    encomiendas = Encomienda.objects.select_related(
        'cliente', 'oficina_origen', 'oficina_destino'
    ).all().order_by('-fecha_registro')

    # Aplicar filtros si existen
    if fecha_inicio:
        encomiendas = encomiendas.filter(fecha_registro__date__gte=fecha_inicio)
    if fecha_fin:
        encomiendas = encomiendas.filter(fecha_registro__date__lte=fecha_fin)
    if estado:
        encomiendas = encomiendas.filter(estado=estado)
    if oficina:
        encomiendas = encomiendas.filter(
            models.Q(oficina_origen_id=oficina) | models.Q(oficina_destino_id=oficina)
        )

    # KPIs Principales
    total_encomiendas = encomiendas.count()
    total_ingresos = encomiendas.aggregate(total=Sum('costo_envio'))['total'] or 0

    # -------------------------------------------------------------
    # Datos para los Gráficos de Chart.js adaptados a Encomiendas
    # -------------------------------------------------------------
    
    # Gráfico 1: Encomiendas por Estado
    encomiendas_por_estado = (
        encomiendas.values('estado')
        .annotate(total=Count('id_encomienda'))
        .order_by('-total')
    )
    # Mapear estados a sus nombres legibles
    estados_dict = dict(Encomienda.ESTADOS_ENCOMIENDA)
    etiquetas_estado = [estados_dict.get(item['estado'], item['estado']) for item in encomiendas_por_estado]
    datos_estado = [item['total'] for item in encomiendas_por_estado]

    # Gráfico 2: Ingresos o Encomiendas por Oficina de Origen
    encomiendas_por_oficina = (
        encomiendas.values('oficina_origen__ciudad', 'oficina_origen__nombre')
        .annotate(total_ingresos=Sum('costo_envio'))
        .order_by('-total_ingresos')[:5] # Top 5 oficinas
    )
    etiquetas_oficina = [f"{item['oficina_origen__ciudad']} - {item['oficina_origen__nombre']}" for item in encomiendas_por_oficina]
    datos_oficina = [float(item['total_ingresos'] or 0) for item in encomiendas_por_oficina]

    # Contexto final
    contexto = {
        "encomiendas": encomiendas,
        "total_encomiendas": total_encomiendas,
        "total_ingresos": total_ingresos,
        "estados_encomienda": Encomienda.ESTADOS_ENCOMIENDA,
        "oficinas": Oficina.objects.all().order_by("ciudad"),
        "filtros": {
            "fecha_inicio": fecha_inicio or "",
            "fecha_fin": fecha_fin or "",
            "estado": estado or "",
            "oficina": oficina or "",
        },
        # JSON para Chart.js
        'etiquetas_estado_json': json.dumps(etiquetas_estado),
        'datos_estado_json': json.dumps(datos_estado),
        'etiquetas_oficina_json': json.dumps(etiquetas_oficina),
        'datos_oficina_json': json.dumps(datos_oficina),
    }

    return render(request, "reportes/reportesGenerales.html", contexto)

# ==========================================
# MÓDULO: Notificaciones (Solo Admin)
# ==========================================
@user_passes_test(es_administrador, login_url="/seguimiento/seguimientoEncomienda/")
def listadoNotificacion(request):
    notificaciones = NotificacionCorreo.objects.select_related("encomienda").all().order_by("-fecha_envio")
    return render(request, "notificaciones/listadoNotificacion.html", {"notificaciones": notificaciones})
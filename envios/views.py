from django.shortcuts import render, redirect
from envios.models import Cliente, Oficina, Transporte, Seguro, Encomienda, Reporte, NotificacionCorreo
from django.contrib import messages

# Create your views here.
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


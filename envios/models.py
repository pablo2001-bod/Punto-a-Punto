from django.db import models



class Cliente(models.Model):
    id_cliente = models.AutoField(primary_key=True)
    cedula = models.CharField(max_length=10, unique=True)
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    email = models.EmailField()
    telefono = models.CharField(max_length=15)
    direccion = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.nombres} {self.apellidos}"


class Oficina(models.Model):
    id_oficina = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=150)
    ciudad = models.CharField(max_length=100)
    direccion = models.CharField(max_length=200)
    telefono = models.CharField(max_length=15)
    email = models.EmailField(blank=True)

    def __str__(self):
        return f"{self.nombre} - {self.ciudad}"


class Transporte(models.Model):

    TIPOS_TRANSPORTE = [
        ("MOTO", "Motocicleta"),
        ("CAMIONETA", "Camioneta"),
        ("CAMION", "Camión"),
    ]

    ESTADOS_TRANSPORTE = [
        ("DISPONIBLE", "Disponible"),
        ("EN_RUTA", "En ruta"),
        ("MANTENIMIENTO", "En mantenimiento"),
    ]

    id_transporte = models.AutoField(primary_key=True)
    placa = models.CharField(max_length=10, unique=True)
    tipo = models.CharField(max_length=20, choices=TIPOS_TRANSPORTE)
    marca = models.CharField(max_length=100)
    modelo = models.CharField(max_length=100)
    capacidad_kg = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=20, choices=ESTADOS_TRANSPORTE,default="DISPONIBLE")

    def __str__(self):
        return f"{self.placa} - {self.tipo}"


class Seguro(models.Model):
    id_seguro = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField()
    porcentaje_cobertura = models.DecimalField(max_digits=5, decimal_places=2)
    costo = models.DecimalField(max_digits=10, decimal_places=2)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre


class Encomienda(models.Model):

    ESTADOS_ENCOMIENDA = [
        ("REGISTRADA", "Registrada"),
        ("OFICINA_ORIGEN", "En oficina de origen"),
        ("EN_TRANSITO", "En tránsito"),
        ("OFICINA_DESTINO", "En oficina de destino"),
        ("ENTREGADA", "Entregada"),
        ("CANCELADA", "Cancelada"),
    ]

    id_encomienda = models.AutoField(primary_key=True)

    codigo_seguimiento = models.CharField(max_length=30, unique=True)

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name="encomiendas")
    oficina_origen = models.ForeignKey(Oficina, on_delete=models.CASCADE, related_name="encomiendas_origen")
    oficina_destino = models.ForeignKey(Oficina, on_delete=models.CASCADE, related_name="encomiendas_destino")
    transporte = models.ForeignKey(Transporte, on_delete=models.SET_NULL, null=True, blank=True, related_name="encomiendas")
    seguro = models.ForeignKey(Seguro, on_delete=models.SET_NULL, null=True, blank=True, related_name="encomiendas")

    nombre_destinatario = models.CharField(max_length=150)
    cedula_destinatario = models.CharField(max_length=10)
    email_destinatario = models.EmailField()
    telefono_destinatario = models.CharField(max_length=15)
    direccion_destino = models.CharField(max_length=200)

    descripcion = models.TextField()
    peso_kg = models.DecimalField(max_digits=10, decimal_places=2)
    valor_declarado = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    costo_envio = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    estado = models.CharField(max_length=30, choices=ESTADOS_ENCOMIENDA, default="REGISTRADA")
    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_entrega = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.codigo_seguimiento} - {self.nombre_destinatario}"


class Reporte(models.Model):

    TIPOS_REPORTE = [
        ("NOVEDAD", "Novedad"),
        ("RETRASO", "Retraso"),
        ("DANIO", "Daño"),
        ("PERDIDA", "Pérdida"),
        ("ENTREGA", "Entrega"),
    ]

    id_reporte = models.AutoField(primary_key=True)
    encomienda = models.ForeignKey(Encomienda, on_delete=models.CASCADE, related_name="reportes")
    tipo = models.CharField(max_length=20, choices=TIPOS_REPORTE)
    detalle = models.TextField()
    fecha_reporte = models.DateTimeField(auto_now_add=True)
    resuelto = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.tipo} - {self.encomienda.codigo_seguimiento}"


class NotificacionCorreo(models.Model):
    id_notificacion = models.AutoField(primary_key=True)
    encomienda = models.ForeignKey(Encomienda, on_delete=models.CASCADE, related_name="notificaciones")
    destinatario = models.EmailField()
    asunto = models.CharField(max_length=200)
    mensaje = models.TextField()
    fecha_envio = models.DateTimeField(auto_now_add=True)
    enviado = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.destinatario} - {self.encomienda.codigo_seguimiento}"

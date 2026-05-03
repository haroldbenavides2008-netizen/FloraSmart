from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

#  El modelo de Usuario
class Usuario(AbstractUser):
    ROLES = (
        ('floricultor', 'Floricultor / Productor'),
        ('comprador_b2b', 'Comprador Mayorista (B2B)'),
        ('comprador_b2c', 'Cliente Final (B2C)'),
    )
    email = models.EmailField(unique=True)
    rol = models.CharField(max_length=20, choices=ROLES, default='comprador_b2c')
    nombre_empresa_o_finca = models.CharField(max_length=100, blank=True, null=True)

    groups = models.ManyToManyField(
        Group,
        related_name="usuario_set",
        blank=True,
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="usuario_permissions_set",
        blank=True,
    )

    def __str__(self):
        return f"{self.username} - {self.get_rol_display()}"

#El modelo de Producto
class Producto(models.Model):
    floricultor = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='mis_productos')
    nombre_flor = models.CharField(max_length=50)
    variedad = models.CharField(max_length=50, blank=True)
    color = models.CharField(max_length=30)
    precio_por_tallo = models.DecimalField(max_digits=10, decimal_places=2)
    cantidad_disponible = models.PositiveIntegerField()
    descripcion = models.TextField(blank=True)
    fecha_publicacion = models.DateTimeField(auto_now_add=True)
    imagen = models.ImageField(upload_to='productos/', null=True, blank=True)

    def __str__(self):
        return f"{self.nombre_flor} - {self.floricultor.nombre_empresa_o_finca if self.floricultor.nombre_empresa_o_finca else 'Sin Finca'}"

# : El modelo de Pedido
class Pedido(models.Model):
    ESTADOS = (
        ('pendiente', 'Pendiente'),
        ('en_camino', 'En Camino'),
        ('entregado', 'Entregado'),
        ('cancelado', 'Cancelado'),
    )

    cliente = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='mis_pedidos_realizados')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='pedidos_del_producto')
    cantidad = models.PositiveIntegerField(default=1)
    fecha_pedido = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    notas = models.TextField(blank=True, null=True)

    def total_pagar(self):
        return self.cantidad * self.producto.precio_por_tallo

    def __str__(self):
        return f"Pedido #{self.id} - {self.cliente.username}"

# MODELO PARA MENSAJES DEL CHAT
class MensajeChat(models.Model):
    emisor = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='mensajes_enviados')
    receptor = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='mensajes_recibidos')
    contenido = models.TextField()
    fecha_envio = models.DateTimeField(auto_now_add=True)
    leido = models.BooleanField(default=False)

    class Meta:
        ordering = ['fecha_envio']

    def __str__(self):
        return f"Mensaje de {self.emisor.username} a {self.receptor.username}"
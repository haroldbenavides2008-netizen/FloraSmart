from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

# PRIMERO: El modelo de Usuario (el que ya tenías)
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

# SEGUNDO: El modelo de Producto (DEBAJO de Usuario)
class Producto(models.Model):
    # Asegúrate de que esta línea tenga exactamente 4 espacios al inicio
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
        return f"{self.nombre_flor} - {self.floricultor.nombre_empresa_o_finca}"
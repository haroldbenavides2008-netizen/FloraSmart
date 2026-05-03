from django.contrib import admin
from .models import Usuario, Producto, Pedido

# Register DE LA BASE.
admin.site.register(Usuario)
admin.site.register(Producto)
admin.site.register(Pedido)
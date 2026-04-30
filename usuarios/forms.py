from django import forms
from .models import Producto

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre_flor', 'variedad', 'color', 'precio_por_tallo', 'cantidad_disponible', 'descripcion', 'imagen']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
        }
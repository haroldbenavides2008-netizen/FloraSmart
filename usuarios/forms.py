from django import forms
from .models import Producto, Usuario

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre_flor', 'variedad', 'color', 'precio_por_tallo', 'cantidad_disponible', 'descripcion', 'imagen']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
        }


class PerfilForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['nombre_empresa_o_finca', 'first_name', 'last_name', 'email', 'telefono', 'ubicacion', 'bio', 'foto_perfil']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellido'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Correo electrónico'}),
            'nombre_empresa_o_finca': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de Empresa o Finca'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Teléfono'}),
            'ubicacion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ubicación'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Cuéntanos sobre ti o tu negocio'}),
            'foto_perfil': forms.FileInput(attrs={'class': 'form-control'}),
        }
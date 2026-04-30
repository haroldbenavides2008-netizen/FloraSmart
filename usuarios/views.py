from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from .models import Usuario, Producto
from .forms import ProductoForm
from firebase_admin import auth as firebase_auth
from django.contrib.auth import logout 

# 1. VISTA DE REGISTRO
def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        rol = request.POST.get('rol')
        empresa = request.POST.get('empresa')

        try:
            # Crea usuario en Firebase
            firebase_auth.create_user(
                email=email,
                password=password,
                display_name=username
            )

            # Crea usuario en Django
            user = Usuario.objects.create_user(
                username=username,
                email=email,
                password=password,
                rol=rol,
                nombre_empresa_o_finca=empresa
            )
            
            login(request, user)
            return redirect('home')

        except Exception as e:
            return render(request, 'register.html', {'error': str(e)})

    return render(request, 'register.html')

# 2. VISTA DE LOGIN
def login_view(request):
    if request.method == 'POST':
        email_ingresado = request.POST.get('email')
        password_ingresada = request.POST.get('password')
        
        try:
            usuario_obj = Usuario.objects.get(email=email_ingresado)
            user = authenticate(request, username=usuario_obj.username, password=password_ingresada)
            
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                return render(request, 'login.html', {'error': 'Contraseña incorrecta'})
        except Usuario.DoesNotExist:
            return render(request, 'login.html', {'error': 'El correo no está registrado'})
            
    return render(request, 'login.html')

# 3. VISTA DE HOME (Dinamizada por Rol)
def home_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    # Si es floricultor, traemos solo SUS productos para su dashboard
    contexto = {}
    if request.user.rol == 'floricultor':
        contexto['mis_productos'] = Producto.objects.filter(floricultor=request.user)
    else:
        # Si es comprador, traemos TODOS los productos del mercado
        contexto['productos_mercado'] = Producto.objects.all()
        
    return render(request, 'home.html', contexto)

# 4. NUEVA VISTA: AGREGAR PRODUCTO
def agregar_producto(request):
    if not request.user.is_authenticated or request.user.rol != 'floricultor':
        return redirect('home')

    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES) # FILES es clave para la foto de la flor
        if form.is_valid():
            producto = form.save(commit=False)
            producto.floricultor = request.user # Trazabilidad: asignamos el producto a esta finca
            producto.save()
            return redirect('home')
    else:
        form = ProductoForm()
        
    return render(request, 'agregar_producto.html', {'form': form})
def logout_view(request):
    logout(request)
    return redirect('login') # Lo enviamos de vuelta al login tras salir
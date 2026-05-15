from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.decorators import login_required

# Importación de modelos y formularios
from .models import Usuario, Producto, Pedido, MensajeChat
from .forms import ProductoForm

# 1. VISTA DE REGISTRO (SIN FIREBASE)
def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        rol = request.POST.get('rol')
        empresa = request.POST.get('empresa')

        try:
            # Creamos el usuario directamente en Django
            # El email ya no chocará con Firebase
            user = Usuario.objects.create_user(
                username=username,
                email=email,
                password=password,
                rol=rol,
                nombre_empresa_o_finca=empresa
            )
            
            login(request, user)
            messages.success(request, f"¡Bienvenida a FloraSmart, {username}!")
            return redirect('home')
        except Exception as e:
            # Ahora el error nos dirá exactamente qué campo de Django falló
            return render(request, 'register.html', {'error': f"Error: {e}"})

    return render(request, 'register.html')

# 2. VISTA DE LOGIN (ESTÁNDAR DE DJANGO)
def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        email_ingresado = request.POST.get('email')
        password_ingresada = request.POST.get('password')
        
        try:
            # Buscamos por email para obtener el username de Django
            usuario_obj = Usuario.objects.get(email=email_ingresado)
            user = authenticate(request, username=usuario_obj.username, password=password_ingresada)
            
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                messages.error(request, "Contraseña incorrecta")
        except Usuario.DoesNotExist:
            messages.error(request, "El correo no está registrado")
            
    return render(request, 'login.html')

# 3. VISTA DE HOME
def home_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    contexto = {}
    if request.user.rol == 'floricultor':
        contexto['mis_productos'] = Producto.objects.filter(floricultor=request.user)
    else:
        contexto['productos_recientes'] = Producto.objects.all().order_by('-fecha_publicacion')[:4]
        
    return render(request, 'home.html', contexto)

# 4. AGREGAR PRODUCTO (GESTIÓN FLORICULTOR)
def agregar_producto(request):
    if not request.user.is_authenticated or request.user.rol != 'floricultor':
        messages.warning(request, "Solo los floricultores pueden agregar productos.")
        return redirect('home')

    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES) 
        if form.is_valid():
            producto = form.save(commit=False)
            producto.floricultor = request.user 
            producto.save()
            messages.success(request, "Producto publicado exitosamente.")
            return redirect('home')
    else:
        form = ProductoForm()
        
    return render(request, 'agregar_productos.html', {'form': form})

# 5. LOGOUT
def logout_view(request):
    logout(request)
    messages.info(request, "Has cerrado sesión correctamente.")
    return redirect('login') 

# 6. VISTA DEL MERCADO 
def mercado_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
        
    productos = Producto.objects.all().order_by('-fecha_publicacion')
    
    # Obtener categorías y colores únicos para los filtros
    categorias = Producto.objects.values_list('nombre_flor', flat=True).distinct().order_by('nombre_flor')
    colores = Producto.objects.values_list('color', flat=True).distinct().order_by('color')
    
    # Crear mapeo de flores a colores para filtrado automático
    flores_colores = {}
    for categoria in categorias:
        flores_colores[categoria] = list(
            Producto.objects.filter(nombre_flor=categoria)
                   .values_list('color', flat=True)
                   .distinct()
                   .order_by('color')
        )
    
    contexto = {
        'productos': productos,
        'categorias': categorias,
        'colores': colores,
        'flores_colores': flores_colores
    }
    return render(request, 'mercado.html', contexto)

# 7. REALIZAR PEDIDO
def realizar_pedido(request, producto_id):
    if not request.user.is_authenticated:
        messages.error(request, "Debes iniciar sesión para comprar.")
        return redirect('login')

    if request.method == 'POST':
        producto = get_object_or_404(Producto, id=producto_id)
        
        if producto.floricultor == request.user:
            messages.error(request, "No puedes comprar tus propios productos.")
            return redirect('mercado')

        # Obtener cantidad del POST (del modal), por defecto 1
        cantidad = int(request.POST.get('cantidad', 1))
        direccion = request.POST.get('direccion_entrega', '').strip()
        notas_adicionales = request.POST.get('notas_adicionales', '').strip()

        if not direccion:
            messages.error(request, "Debes ingresar la dirección de entrega para completar la compra.")
            return redirect('mercado')

        if producto.cantidad_disponible <= 0:
            messages.error(request, "No hay stock disponible para este producto.")
            return redirect('mercado')
        
        # Validar cantidad
        if cantidad < 1:
            cantidad = 1
        if cantidad > producto.cantidad_disponible:
            cantidad = producto.cantidad_disponible

        notas_finales = f"Dirección de entrega: {direccion}"
        if notas_adicionales:
            notas_finales += f" | Notas: {notas_adicionales}"

        Pedido.objects.create(
            cliente=request.user,
            producto=producto,
            cantidad=cantidad,
            notas=notas_finales
        )

        producto.cantidad_disponible = max(producto.cantidad_disponible - cantidad, 0)
        producto.save()
        
        messages.success(request, f"¡Pedido solicitado! Has pedido {cantidad} tallo(s) de {producto.nombre_flor}.")
        return redirect('mis_pedidos')

    return redirect('mercado')

# 8. VISTA DE MIS PEDIDOS / PEDIDOS RECIBIDOS
def mis_pedidos_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    if request.user.rol == 'floricultor':
        pedidos = Pedido.objects.filter(producto__floricultor=request.user).order_by('-fecha_pedido')
        titulo = "Pedidos Recibidos"
    else:
        pedidos = Pedido.objects.filter(cliente=request.user).order_by('-fecha_pedido')
        titulo = "Mis Pedidos"

    for pedido in pedidos:
        pedido.direccion_entrega = ''
        pedido.notas_adicionales = ''
        if pedido.notas:
            partes = pedido.notas.split(' | Notas: ')
            pedido.direccion_entrega = partes[0].replace('Dirección de entrega: ', '').strip()
            if len(partes) > 1:
                pedido.notas_adicionales = partes[1].strip()

    return render(request, 'mis_pedidos.html', {'pedidos': pedidos, 'titulo': titulo})

# 9. VISTA DE LISTA DE CHATS
@login_required
def lista_chats_view(request):
    """
    Muestra la lista de usuarios con los que el usuario actual puede chatear.
    """
    if request.user.rol == 'floricultor':
        # Para floricultores: mostrar clientes que han comprado sus productos
        usuarios_chat = Usuario.objects.filter(
            mis_pedidos_realizados__producto__floricultor=request.user
        ).distinct().order_by('-mis_pedidos_realizados__fecha_pedido')
    else:
        # Para clientes: mostrar floricultores cuyas flores han comprado
        usuarios_chat = Usuario.objects.filter(
            mis_productos__pedidos_del_producto__cliente=request.user,
            rol='floricultor'
        ).distinct().order_by('-mis_productos__pedidos_del_producto__fecha_pedido')
    
    contexto = {
        'usuarios': usuarios_chat,
        'titulo': 'Chats'
    }
    return render(request, 'lista_chats.html', contexto)

# 10. VISTA DE CHAT INTEGRADA
@login_required
def chat_view(request, receptor_id):
    """
    Gestiona la comunicación en tiempo real entre compradores y floricultores de FloraSmart.
    """
    receptor = get_object_or_404(Usuario, id=receptor_id)
    
    if receptor == request.user:
        messages.warning(request, "No puedes chatear contigo mismo.")
        return redirect('lista_chats')

    # Generamos un ID de sala único y consistente
    ids_ordenados = sorted([request.user.id, receptor.id])
    sala_id = f"chat_{ids_ordenados[0]}_{ids_ordenados[1]}"
    
    # Si es POST, guardar el mensaje
    if request.method == 'POST':
        contenido = request.POST.get('contenido', '').strip()
        if contenido:
            MensajeChat.objects.create(
                emisor=request.user,
                receptor=receptor,
                contenido=contenido
            )
        return redirect('chat', receptor_id=receptor_id)
    
    # Obtener todos los mensajes entre estos dos usuarios
    mensajes = MensajeChat.objects.filter(
        (Q(emisor=request.user) & Q(receptor=receptor)) |
        (Q(emisor=receptor) & Q(receptor=request.user))
    ).order_by('fecha_envio')
    
    contexto = {
        'receptor': receptor,
        'sala_id': sala_id,
        'titulo': f"Chat con {receptor.username}",
        'mensajes': mensajes
    }
    
    return render(request, 'chat.html', contexto)

# 11. VISTA PARA CANCELAR PEDIDO
@login_required
def cancelar_pedido(request, pedido_id):
    """
    Cancela un pedido si está en estado 'pendiente'.
    Solo acepta POST por seguridad.
    """
    if request.method != 'POST':
        messages.error(request, "Método no permitido.")
        return redirect('mis_pedidos')
    
    pedido = get_object_or_404(Pedido, id=pedido_id)
    
    # Verificar que el usuario sea el cliente del pedido
    if pedido.cliente != request.user:
        messages.error(request, "No tienes permiso para cancelar este pedido.")
        return redirect('mis_pedidos')
    
    # Solo permitir cancelación si está pendiente
    if pedido.estado != 'pendiente':
        messages.error(request, "Solo puedes cancelar pedidos en estado 'pendiente'.")
        return redirect('mis_pedidos')
    
    # Cambiar estado a cancelado y devolver stock
    pedido.estado = 'cancelado'
    pedido.save()
    
    # Devolver la cantidad al stock del producto
    pedido.producto.cantidad_disponible += pedido.cantidad
    pedido.producto.save()
    
    messages.success(request, "Pedido cancelado exitosamente.")
    return redirect('mis_pedidos')

# 12. VISTA PARA EDITAR PEDIDO
@login_required
def editar_pedido(request, pedido_id):
    """
    Permite editar cantidad, dirección y notas de un pedido en estado 'pendiente'.
    """
    pedido = get_object_or_404(Pedido, id=pedido_id)
    
    # Verificar que el usuario sea el cliente del pedido
    if pedido.cliente != request.user:
        messages.error(request, "No tienes permiso para editar este pedido.")
        return redirect('mis_pedidos')
    
    # Solo permitir edición si está pendiente
    if pedido.estado != 'pendiente':
        messages.error(request, "Solo puedes editar pedidos en estado 'pendiente'.")
        return redirect('mis_pedidos')
    
    if request.method == 'POST':
        try:
            nueva_cantidad = int(request.POST.get('cantidad', pedido.cantidad))
        except (ValueError, TypeError):
            nueva_cantidad = pedido.cantidad
            
        direccion = request.POST.get('direccion_entrega', '').strip()
        notas_adicionales = request.POST.get('notas_adicionales', '').strip()
        
        # Validar cantidad
        if nueva_cantidad < 1:
            messages.error(request, "La cantidad debe ser al menos 1.")
            return redirect('editar_pedido', pedido_id=pedido_id)
        
        if not direccion:
            messages.error(request, "Debes ingresar la dirección de entrega.")
            return redirect('editar_pedido', pedido_id=pedido_id)
        
        # Calcular diferencia de cantidad para ajustar stock
        diferencia = nueva_cantidad - pedido.cantidad
        
        # Validar que hay suficiente stock si la cantidad aumenta
        if diferencia > 0 and pedido.producto.cantidad_disponible < diferencia:
            messages.error(request, f"Solo hay {pedido.producto.cantidad_disponible} unidades disponibles.")
            return redirect('editar_pedido', pedido_id=pedido_id)
        
        # Actualizar stock
        pedido.producto.cantidad_disponible -= diferencia
        pedido.producto.save()
        
        # Actualizar pedido
        pedido.cantidad = nueva_cantidad
        notas_finales = f"Dirección de entrega: {direccion}"
        if notas_adicionales:
            notas_finales += f" | Notas: {notas_adicionales}"
        pedido.notas = notas_finales
        pedido.save()
        
        messages.success(request, "Pedido actualizado exitosamente.")
        return redirect('mis_pedidos')
    
    # Preparar datos para la plantilla (GET)
    if pedido.notas:
        partes = pedido.notas.split(' | Notas: ')
        direccion_entrega = partes[0].replace('Dirección de entrega: ', '').strip()
        notas_adicionales = partes[1].strip() if len(partes) > 1 else ''
    else:
        direccion_entrega = ''
        notas_adicionales = ''
    
    contexto = {
        'pedido': pedido,
        'direccion_entrega': direccion_entrega,
        'notas_adicionales': notas_adicionales,
        'stock_disponible': pedido.producto.cantidad_disponible + pedido.cantidad
    }
    
    return render(request, 'editar_pedido.html', contexto)
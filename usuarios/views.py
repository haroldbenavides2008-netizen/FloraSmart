import json
import uuid
import requests

from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.db.models import Q
from django.conf import settings
from django.utils import timezone
from django.http import HttpResponse, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required

# Importación de modelos y formularios
from .models import Usuario, Producto, Pedido, MensajeChat
from .forms import ProductoForm, PerfilForm

# 1. VISTA DE REGISTRO (SIN FIREBASE)
def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        rol = request.POST.get('rol')
        empresa = request.POST.get('empresa')

        try:
            # Creamos el usuario directamente en Django
            user = Usuario.objects.create_user(
                username=username,
                email=email,
                password=password,
                rol=rol,
                nombre_empresa_o_finca=empresa
            )

            # Autenticamos el usuario recién creado antes de iniciar sesión
            authenticated_user = authenticate(request, username=username, password=password)
            if authenticated_user is not None:
                login(request, authenticated_user)
                messages.success(request, f"¡Bienvenida a FloraSmart, {username}!")
                return redirect('home')

            return render(request, 'register.html', {'error': 'No se pudo iniciar sesión automáticamente. Intenta iniciar sesión manualmente.'})
        except Exception as e:
            return render(request, 'register.html', {'error': f"Error: {e}"})

    return render(request, 'register.html')

# 2. VISTA DE LOGIN (ESTÁNDAR DE DJANGO)
def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        email_ingresado = request.POST.get('email')
        password_ingresada = request.POST.get('password')

        print("EMAIL:", email_ingresado)

        try:
            usuario_obj = Usuario.objects.get(email=email_ingresado)

            print("USUARIO:", usuario_obj.username)

            user = authenticate(
                request,
                username=usuario_obj.username,
                password=password_ingresada
            )

            print("AUTH:", user)

            if user is not None:
                login(request, user)
                return redirect('home')

            messages.error(request, "Contraseña incorrecta")

        except Usuario.DoesNotExist:
            print("USUARIO NO EXISTE")
            messages.error(request, "El correo no está registrado")

    return render(request, 'login.html')

# 3. VISTA DE HOME
def home_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    contexto = {}
    if request.user.rol != 'floricultor':
        contexto['productos_mercado'] = Producto.objects.all().order_by('-fecha_publicacion')[:4]
    return render(request, 'home.html', contexto)

# 3.1. VISTA 'MIS PRODUCTOS' (PÁGINA SEPARADA PARA FLORICULTORES)
@login_required
def mis_productos_view(request):
    if request.user.rol != 'floricultor':
        messages.warning(request, "Solo los floricultores pueden ver esta sección.")
        return redirect('home')

    mis_productos = Producto.objects.filter(floricultor=request.user).order_by('-fecha_publicacion')
    return render(request, 'mis_productos.html', {'mis_productos': mis_productos})

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
    # Los floricultores no deben ver el mercado
    if hasattr(request.user, 'rol') and request.user.rol == 'floricultor':
        messages.info(request, "Acceso al mercado no disponible para floricultores.")
        return redirect('mis_pedidos')
        
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

# 7.1. VISTA PARA REALIZAR PEDIDO CON VARIOS PRODUCTOS
@login_required
def realizar_pedido_carrito(request):
    if request.method != 'POST':
        return redirect('mercado')

    cart_data = request.POST.get('cart_data', '').strip()
    direccion = request.POST.get('direccion_entrega', '').strip()
    notas_adicionales = request.POST.get('notas_adicionales', '').strip()

    if not cart_data:
        messages.error(request, "No hay productos en el carrito para procesar el pedido.")
        return redirect('mercado')

    if not direccion:
        messages.error(request, "Debes ingresar la dirección de entrega para completar la compra.")
        return redirect('mercado')

    try:
        cart_items = json.loads(cart_data)
    except json.JSONDecodeError:
        messages.error(request, "Los datos del carrito no son válidos.")
        return redirect('mercado')

    if not isinstance(cart_items, list) or not cart_items:
        messages.error(request, "No hay productos válidos en el carrito.")
        return redirect('mercado')

    pedido_grupo = uuid.uuid4()
    cantidad_total = 0
    productos_pedidos = []

    notas_finales = f"Dirección de entrega: {direccion}"
    if notas_adicionales:
        notas_finales += f" | Notas: {notas_adicionales}"

    for item in cart_items:
        producto_id = item.get('id')
        cantidad = int(item.get('cantidad', 1)) if item.get('cantidad') else 1
        if cantidad < 1:
            cantidad = 1

        producto = get_object_or_404(Producto, id=producto_id)
        if producto.floricultor == request.user:
            messages.error(request, "No puedes comprar tus propios productos.")
            return redirect('mercado')

        if producto.cantidad_disponible <= 0:
            messages.error(request, f"No hay stock disponible para {producto.nombre_flor}.")
            return redirect('mercado')

        if cantidad > producto.cantidad_disponible:
            cantidad = producto.cantidad_disponible

        Pedido.objects.create(
            cliente=request.user,
            producto=producto,
            cantidad=cantidad,
            notas=notas_finales,
            pedido_grupo=pedido_grupo
        )

        producto.cantidad_disponible = max(producto.cantidad_disponible - cantidad, 0)
        producto.save()

        cantidad_total += cantidad
        productos_pedidos.append(producto.nombre_flor)

    mensaje_productos = ', '.join(productos_pedidos[:3])
    if len(productos_pedidos) > 3:
        mensaje_productos += f" y {len(productos_pedidos) - 3} más"

    messages.success(request, f"¡Pedido solicitado! Has pedido {cantidad_total} tallo(s) de {mensaje_productos}.")
    return redirect('mis_pedidos')

# Helpers para pagos Wompi

def calcular_total_pedido(pedidos):
    return sum(item.cantidad * item.producto.precio_por_tallo for item in pedidos)


def obtener_aceptance_token(public_key):
    url = f"{settings.WOMPI_SANDBOX_URL}/v1/merchants/{public_key}/acceptance_token"
    response = requests.get(url, timeout=10)
    if response.status_code == 404:
        raise ValueError('La cuenta Wompi sandbox aún no está activada o la llave pública no es válida. Verifica en el dashboard de Wompi que tu comercio esté aprobado.')
    if response.status_code == 401:
        raise ValueError('Autenticación inválida de Wompi. Revisa la llave pública y la llave privada en tu .env.')
    if response.status_code == 403:
        raise ValueError('Acceso denegado a Wompi. Tu cuenta sandbox puede estar en revisión o no tener permisos suficientes.')
    response.raise_for_status()
    return response.json().get('data', {}).get('presigned_acceptance_token')


def obtener_pedidos_grupo(pedido):
    if pedido.pedido_grupo:
        return list(Pedido.objects.filter(pedido_grupo=pedido.pedido_grupo))
    return [pedido]


def pagar_pedido(request, pedido_id):
    if not request.user.is_authenticated:
        return redirect('login')

    pedido = get_object_or_404(Pedido, id=pedido_id, cliente=request.user)
    if pedido.estado != 'pendiente':
        messages.error(request, 'Solo es posible pagar pedidos pendientes.')
        return redirect('mis_pedidos')

    if pedido.estado_pago == 'pagado':
        messages.info(request, 'Este pedido ya está pagado.')
        return redirect('mis_pedidos')

    pedidos = obtener_pedidos_grupo(pedido)
    total = calcular_total_pedido(pedidos)
    reference = f"pedido-{pedido.id}-{pedido.pedido_grupo or pedido.id}"

    try:
        acceptance_token = obtener_aceptance_token(settings.WOMPI_PUBLIC_KEY)
        if not acceptance_token:
            raise ValueError('No se obtuvo el token de aceptación de Wompi.')

        payload = {
            'acceptance_token': acceptance_token,
            'amount_in_cents': int(total * 100),
            'currency': 'COP',
            'customer_email': request.user.email,
            'payment_method': {'type': 'NEQUI'},
            'reference': reference,
            'redirect_url': settings.WOMPI_REDIRECT_URL,
            'metadata': {
                'pedido_id': str(pedido.id),
                'pedido_grupo': str(pedido.pedido_grupo) if pedido.pedido_grupo else '',
            }
        }

        response = requests.post(
            f"{settings.WOMPI_SANDBOX_URL}/v1/transactions",
            json=payload,
            headers={'Authorization': f'Bearer {settings.WOMPI_PRIVATE_KEY}'},
            timeout=10
        )
        response.raise_for_status()
        data = response.json().get('data', {})
        transaction = data.get('transaction', data)

        pedido.wompi_transaction_id = transaction.get('id')
        pedido.wompi_reference = reference
        pedido.estado_pago = 'pendiente'
        pedido.save()

        redirect_url = transaction.get('redirect_url') or data.get('presigned_acceptance_url') or data.get('payment_method', {}).get('type')
        if redirect_url:
            return redirect(redirect_url)

        messages.error(request, 'No se pudo generar la página de pago de Wompi. Intenta de nuevo más tarde.')
    except Exception as exc:
        messages.error(request, f"Error al crear pago con Wompi: {exc}")

    return redirect('mis_pedidos')


def wompi_retorno(request):
    messages.success(request, 'Tu pago está en proceso de verificación. Si fue aprobado, el pedido se actualizará pronto.')
    return redirect('mis_pedidos')


def wompi_webhook(request):
    if request.method != 'POST':
        return HttpResponseBadRequest('Método no permitido')

    try:
        payload = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        return HttpResponseBadRequest('JSON inválido')

    event_data = payload.get('data', {})
    transaction = event_data.get('transaction', event_data)
    reference = transaction.get('reference')
    status = transaction.get('status')

    if not reference:
        return HttpResponseBadRequest('Referencia ausente')

    pedidos = Pedido.objects.filter(wompi_reference=reference)
    if not pedidos.exists() and '-' in reference:
        ref_parts = reference.split('-', 2)
        if len(ref_parts) >= 2:
            pedido_id = ref_parts[1]
            pedidos = Pedido.objects.filter(id=pedido_id)

    if not pedidos.exists():
        return HttpResponse('Pedido no encontrado', status=404)

    if status == 'APPROVED':
        for item in pedidos:
            item.estado_pago = 'pagado'
            item.save()
        return HttpResponse('Pago aprobado')

    if status in ['DECLINED', 'ERROR', 'VOIDED']:
        for item in pedidos:
            if item.estado == 'pendiente':
                item.estado = 'cancelado'
                item.estado_pago = 'cancelado'
                item.producto.cantidad_disponible += item.cantidad
                item.producto.save()
                item.save()
        return HttpResponse('Pago rechazado, pedido cancelado')

    return HttpResponse('Evento procesado')

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

    ordenes = []
    grupos = {}

    for pedido in pedidos:
        pedido.direccion_entrega = ''
        pedido.notas_adicionales = ''
        if pedido.notas:
            partes = pedido.notas.split(' | Notas: ')
            pedido.direccion_entrega = partes[0].replace('Dirección de entrega: ', '').strip()
            if len(partes) > 1:
                pedido.notas_adicionales = partes[1].strip()

        llave = str(pedido.pedido_grupo) if pedido.pedido_grupo else f'single-{pedido.id}'

        if llave not in grupos:
            grupos[llave] = {
                'clave': llave,
                'representante_id': pedido.id,
                'cliente': pedido.cliente,
                'direccion_entrega': pedido.direccion_entrega,
                'notas_adicionales': pedido.notas_adicionales,
                'fecha_pedido': pedido.fecha_pedido,
                'estado': pedido.estado,
                'items': [],
                'cantidad_total': 0,
                'productos_resumen': '',
            }

        grupos[llave]['items'].append(pedido)
        grupos[llave]['cantidad_total'] += pedido.cantidad

    for orden in grupos.values():
        productos = []
        for item in orden['items']:
            nombre = item.producto.nombre_flor
            if item.producto.variedad:
                nombre += f" {item.producto.variedad}"
            productos.append(nombre)
        orden['productos_resumen'] = ', '.join(productos)
        orden['primer_item'] = orden['items'][0]
        orden['numero_items'] = len(orden['items'])
        # Estado de pago: obtener del primer item (todos deben ser iguales)
        orden['estado_pago'] = orden['items'][0].estado_pago if orden['items'] else 'pendiente'
        orden['total_pagar'] = calcular_total_pedido(orden['items'])

    ordenes = list(grupos.values())
    ordenes.sort(key=lambda o: o['fecha_pedido'], reverse=True)
    pedidos_count = len(ordenes)

    return render(request, 'mis_pedidos.html', {'ordenes': ordenes, 'titulo': titulo, 'pedidos_count': pedidos_count})

# 9. VISTA DE NOTIFICACIONES
@login_required
def notificaciones_view(request):
    """Vista dedicada para que el cliente vea el avance de su pedido."""
    if request.user.rol != 'comprador_b2c':
        return redirect('home')

    ultimo_pedido = Pedido.objects.filter(cliente=request.user).order_by('-fecha_pedido').first()
    contexto = {
        'ultimo_pedido': ultimo_pedido,
    }
    return render(request, 'notificaciones.html', contexto)

# 10. VISTA DE LISTA DE CHATS
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
    
    # Determinar si es un pedido agrupado
    if pedido.pedido_grupo:
        pedidos_a_cancelar = Pedido.objects.filter(pedido_grupo=pedido.pedido_grupo)
    else:
        pedidos_a_cancelar = [pedido]

    # Solo permitir cancelación si todos los pedidos están pendientes
    for item in pedidos_a_cancelar:
        if item.estado != 'pendiente':
            messages.error(request, "Solo puedes cancelar pedidos en estado 'pendiente'.")
            return redirect('mis_pedidos')

    for item in pedidos_a_cancelar:
        item.estado = 'cancelado'
        item.save()
        item.producto.cantidad_disponible += item.cantidad
        item.producto.save()
    
    messages.success(request, "Pedido cancelado exitosamente.")
    return redirect('mis_pedidos')

# 11. VISTA PARA CAMBIAR ESTADO DEL PEDIDO
@login_required
def cambiar_estado_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id, producto__floricultor=request.user)
    if request.method != 'POST':
        messages.error(request, "Método no permitido.")
        return redirect('mis_pedidos')

    nuevo_estado = request.POST.get('estado')
    if nuevo_estado not in ['en_camino', 'entregado']:
        messages.error(request, 'Estado no válido para actualizar el pedido.')
        return redirect('mis_pedidos')

    if pedido.pedido_grupo:
        pedidos_actualizar = Pedido.objects.filter(pedido_grupo=pedido.pedido_grupo)
    else:
        pedidos_actualizar = [pedido]

    if nuevo_estado == 'en_camino':
        if any(item.estado != 'pendiente' for item in pedidos_actualizar):
            messages.error(request, 'Solo puedes marcar pedidos pendientes como "En Camino".')
            return redirect('mis_pedidos')
    elif nuevo_estado == 'entregado':
        if any(item.estado != 'en_camino' for item in pedidos_actualizar):
            messages.error(request, 'Solo puedes marcar pedidos en camino como "Entregado".')
            return redirect('mis_pedidos')

    for item in pedidos_actualizar:
        item.estado = nuevo_estado
        item.save()

    messages.success(request, f"Pedido actualizado a {pedido.get_estado_display()}.")
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
    
    # No permitir edición de pedidos agrupados
    if pedido.pedido_grupo:
        messages.error(request, "No puedes editar un pedido con varios productos. Cancelalo y realiza uno nuevo si necesitas cambiarlo.")
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

# 13. VISTA DE CONFIGURACIÓN
@login_required
def configuracion_view(request):
    """
    Vista para mostrar opciones de tema e idioma.
    """
    if request.method == 'POST':
        theme = request.POST.get('theme', 'light')
        language = request.POST.get('language', 'es')
        request.session['theme'] = theme
        request.session['language'] = language
        messages.success(request, 'Preferencias de configuración guardadas.')
        return redirect('configuracion')

    theme = request.session.get('theme', 'light')
    language = request.session.get('language', 'es')
    contexto = {
        'theme': theme,
        'language': language,
    }

    return render(request, 'configuracion.html', contexto)

# 14. VISTA DE PERFIL DE USUARIO
@login_required
def perfil_view(request):
    """
    Vista para ver y editar el perfil del usuario.
    """
    usuario = request.user
    
    if request.method == 'POST':
        form = PerfilForm(request.POST, request.FILES, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, "¡Perfil actualizado exitosamente!")
            return redirect('perfil')
    else:
        form = PerfilForm(instance=usuario)
    
    if usuario.rol == 'floricultor':
        pedidos_todos = Pedido.objects.filter(producto__floricultor=usuario).order_by('-fecha_pedido')
        total_ventas = sum((pedido.total_pagar() for pedido in pedidos_todos), Decimal('0.00'))
        productos_publicados = usuario.mis_productos.count()
    else:
        pedidos_todos = usuario.mis_pedidos_realizados.order_by('-fecha_pedido')
        total_ventas = None
        productos_publicados = None

    total_pedidos = pedidos_todos.count()
    pedidos_recientes = pedidos_todos[:3]
    pedidos_restantes = pedidos_todos[3:]
    contexto = {
        'form': form,
        'usuario': usuario,
        'pedidos_recientes': pedidos_recientes,
        'pedidos_restantes': pedidos_restantes,
        'total_pedidos': total_pedidos,
        'total_ventas': total_ventas,
        'productos_publicados': productos_publicados,
        'es_floricultor': usuario.rol == 'floricultor',
    }
    
    return render(request, 'perfil.html', contexto)
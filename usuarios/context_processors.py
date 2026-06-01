from .models import Pedido


def order_notifications(request):
    """Context processor para mostrar un aviso del pedido más reciente en el sidebar."""
    if not request.user.is_authenticated or request.user.rol != 'comprador_b2c':
        return {}

    ultimo_pedido = Pedido.objects.filter(cliente=request.user).order_by('-fecha_pedido').first()
    if not ultimo_pedido:
        return {
            'sidebar_order_notification': {
                'mensaje': 'Aquí verás cómo avanza tu pedido.',
                'pedido': None,
                'estado': None,
            }
        }

    if ultimo_pedido.estado == 'pendiente':
        mensaje = 'Tu pedido está pendiente y pronto será procesado.'
    elif ultimo_pedido.estado == 'en_camino':
        mensaje = 'Tu pedido está en camino. Prepárate para recibirlo pronto.'
    elif ultimo_pedido.estado == 'entregado':
        mensaje = 'Tu pedido ya fue entregado. ¡Gracias por comprar con nosotros!'
    elif ultimo_pedido.estado == 'cancelado':
        mensaje = 'Tu pedido fue cancelado. Revisa tus pedidos para más detalles.'
    else:
        mensaje = f'Estado actual: {ultimo_pedido.get_estado_display()}.'

    return {
        'sidebar_order_notification': {
            'mensaje': mensaje,
            'pedido': ultimo_pedido,
            'estado': ultimo_pedido.estado,
        }
    }

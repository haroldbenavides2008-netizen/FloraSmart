"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
"""
URL configuration for core project.
"""

from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from usuarios import views

urlpatterns = [
    # Página principal
    path('', RedirectView.as_view(url='/home/', permanent=False)),

    # Administración
    path('admin/', admin.site.urls),

    # Autenticación
    path('login/', views.login_view, name='login'),
    path('registro/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),

    # Aplicación principal
    path('home/', views.home_view, name='home'),
    path('agregar-producto/', views.agregar_producto, name='agregar_producto'),
    path('mis-productos/', views.mis_productos_view, name='mis_productos'),
    path('configuracion/', views.configuracion_view, name='configuracion'),
    path('perfil/', views.perfil_view, name='perfil'),

    # Mercado y pedidos
    path('mercado/', views.mercado_view, name='mercado'),
    path('realizar-pedido/<int:producto_id>/', views.realizar_pedido, name='realizar_pedido'),
    path('realizar-pedido-carrito/', views.realizar_pedido_carrito, name='realizar_pedido_carrito'),
    path('pedidos/<int:pedido_id>/pagar/', views.pagar_pedido, name='pagar_pedido'),

    # Mercado Pago Webhook
    path('pagos/mercadopago/webhook/', views.mercadopago_webhook, name='mercadopago_webhook'),

    # Pedidos
    path('mis-pedidos/', views.mis_pedidos_view, name='mis_pedidos'),
    path('notificaciones/', views.notificaciones_view, name='notificaciones'),
    path('cancelar-pedido/<int:pedido_id>/', views.cancelar_pedido, name='cancelar_pedido'),
    path('cambiar-estado-pedido/<int:pedido_id>/', views.cambiar_estado_pedido, name='cambiar_estado_pedido'),
    path('editar-pedido/<int:pedido_id>/', views.editar_pedido, name='editar_pedido'),

    # Chat
    path('chats/', views.lista_chats_view, name='lista_chats'),
    path('chat/<int:receptor_id>/', views.chat_view, name='chat'),
]

# Archivos multimedia
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



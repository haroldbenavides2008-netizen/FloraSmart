from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Pedido, Producto


@override_settings(
    STORAGES={
        'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
        'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
    }
)
class PedidoStatusTests(TestCase):
    def test_floricultor_sees_status_actions_without_payment_gate(self):
        User = get_user_model()
        floricultor = User.objects.create_user(
            username='florista',
            email='florista@example.com',
            password='secret123',
            rol='floricultor',
        )
        cliente = User.objects.create_user(
            username='cliente',
            email='cliente@example.com',
            password='secret123',
            rol='comprador_b2c',
        )
        producto = Producto.objects.create(
            floricultor=floricultor,
            nombre_flor='Rosa',
            color='Rojo',
            precio_por_tallo=10,
            cantidad_disponible=5,
        )
        Pedido.objects.create(
            cliente=cliente,
            producto=producto,
            cantidad=2,
            estado='pendiente',
            estado_pago='pendiente',
        )

        self.client.force_login(floricultor)
        response = self.client.get(reverse('mis_pedidos'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'En Camino')
        self.assertContains(response, 'name="estado" value="en_camino"')
        self.assertNotContains(response, 'Esperando pago')
        self.assertNotContains(response, 'Pago')

    def test_cliente_ve_el_estado_actualizado_al_cambiarlo(self):
        User = get_user_model()
        floricultor = User.objects.create_user(
            username='florista2',
            email='florista2@example.com',
            password='secret123',
            rol='floricultor',
        )
        cliente = User.objects.create_user(
            username='cliente2',
            email='cliente2@example.com',
            password='secret123',
            rol='comprador_b2c',
        )
        producto = Producto.objects.create(
            floricultor=floricultor,
            nombre_flor='Tulipán',
            color='Amarillo',
            precio_por_tallo=12,
            cantidad_disponible=3,
        )
        pedido = Pedido.objects.create(
            cliente=cliente,
            producto=producto,
            cantidad=1,
            estado='pendiente',
            estado_pago='pendiente',
        )

        self.client.force_login(floricultor)
        self.client.post(
            reverse('cambiar_estado_pedido', args=[pedido.id]),
            {'estado': 'en_camino'},
        )

        self.client.force_login(cliente)
        response = self.client.get(reverse('mis_pedidos'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'En Camino')

# Integración de Pagos Wompi en FloraSmart

## Descripción General
Este documento describe cómo configurar y usar la integración de Wompi para procesar pagos en FloraSmart.

## Flujo de Pagos
1. **Cliente crea pedido** → Pedido se marca como "pendiente" con estado de pago "pendiente"
2. **Cliente ve opción "Pagar"** → En Mis Pedidos, solo si el estado de pago es "pendiente"
3. **Cliente hace clic en "Pagar"** → Se redirige a Wompi
4. **Cliente completa pago** → Wompi procesa la transacción
5. **Webhook recibe respuesta** → FloraSmart actualiza el estado del pedido:
   - Si está **APPROVED**: `estado_pago = 'pagado'` (El floricultor puede confirmar)
   - Si está **DECLINED/ERROR**: `estado = 'cancelado'`, `estado_pago = 'cancelado'` (Stock se devuelve)
6. **Floricultor ve pedidos pagados** → Solo puede confirmar pedidos con `estado_pago = 'pagado'`

## Configuración Paso a Paso

### 1. Registrarse en Wompi
- Visita https://sandbox.wompi.co (para pruebas)
- Crea una cuenta y obtén tus credenciales
- Copia tu **PUBLIC_KEY** y **PRIVATE_KEY**

### 2. Configurar Variables de Entorno
Crea un archivo `.env` en la raíz del proyecto (copiar desde `.env.example`):

```bash
WOMPI_PUBLIC_KEY=your_public_key_here
WOMPI_PRIVATE_KEY=your_private_key_here
WOMPI_REDIRECT_URL=http://localhost:8000/pagos/wompi/retorno/
WOMPI_WEBHOOK_URL=http://localhost:8000/pagos/wompi/webhook/
```

Para producción, actualiza las URLs con tu dominio real.

### 3. Instalar Dependencias
```bash
pip install requests python-dotenv
```

### 4. Ejecutar Migraciones
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Configurar Webhook en Wompi Dashboard
- Ve al dashboard de Wompi
- En Configuración → Webhooks, añade:
  - URL: `https://tudominio.com/pagos/wompi/webhook/`
  - Eventos: Selecciona "transaction.approved", "transaction.declined", etc.

### 6. Cargar Variables de Entorno en Django
Modifica `core/settings.py` si necesitas cargar desde archivo `.env`:
```python
import os
from dotenv import load_dotenv

load_dotenv()
WOMPI_PUBLIC_KEY = os.getenv('WOMPI_PUBLIC_KEY')
WOMPI_PRIVATE_KEY = os.getenv('WOMPI_PRIVATE_KEY')
```

## Flujo de Datos del Pago

### Tabla `Pedido` - Nuevos Campos:
- `estado_pago`: 'pendiente', 'pagado', 'rechazado', 'cancelado'
- `wompi_transaction_id`: ID de la transacción en Wompi
- `wompi_reference`: Referencia única del pago (formato: `pedido-{id}-{grupo}`)

### Endpoints

#### POST `/pedidos/<id>/pagar/`
- Valida que el pedido esté pendiente
- Obtiene el token de aceptación de Wompi
- Crea la transacción en Wompi
- Redirige a la página de pago de Wompi

#### GET `/pagos/wompi/retorno/`
- Endpoint de retorno tras pagar (Wompi redirige aquí)
- Muestra mensaje de verificación

#### POST `/pagos/wompi/webhook/`
- Recibe eventos del webhook de Wompi
- Valida la referencia del pedido
- Actualiza estados según respuesta:
  - **APPROVED**: Marca como pagado
  - **DECLINED/ERROR**: Cancela pedido y devuelve stock

## Lógica de Negocio

### Estados del Pedido vs Estado de Pago

| Estado Pedido | Estado Pago | Acción | Quién lo ve |
|---|---|---|---|
| pendiente | pendiente | Cliente puede pagar o cancelar | Cliente |
| pendiente | pagado | Floricultor puede marcar como "En Camino" | Ambos |
| pendiente | cancelado | Pedido no disponible | Cliente (cancelado) |
| en_camino | pagado | Floricultor marca como entregado | Ambos |
| entregado | pagado | Pedido completado | Ambos |

### Acciones Disponibles

**Para Clientes:**
- Si `estado='pendiente'` y `estado_pago='pendiente'`: Pagar, Editar, Cancelar
- Si `estado='pendiente'` y `estado_pago='pagado'`: Solo ver detalles
- Si `estado='en_camino'` o `estado='entregado'`: Solo ver detalles

**Para Floricultores:**
- Si `estado_pago != 'pagado'`: Ver advertencia "Esperando pago"
- Si `estado_pago='pagado'` y `estado='pendiente'`: Marcar como "En Camino"
- Si `estado_pago='pagado'` y `estado='en_camino'`: Marcar como "Entregado"

## Pruebas con Sandbox de Wompi

### Tarjetas de Prueba
- **Exitoso**: 4242 4242 4242 4242
- **Rechazado**: 4111 1111 1111 1111
- Cualquier fecha futura y CVC válido

### Cómo Probar
1. Ve a Mercado y crea un pedido
2. En Mis Pedidos, haz clic en "Pagar"
3. Serás redirigido a Wompi
4. Usa una tarjeta de prueba
5. Completa el pago
6. Serás redirigido de vuelta a `/pagos/wompi/retorno/`

### Verificar Estados
```python
from usuarios.models import Pedido
pedidos = Pedido.objects.filter(cliente__username='cliente')
for p in pedidos:
    print(f"Pedido {p.id}: {p.estado} - Pago: {p.estado_pago}")
```

## Troubleshooting

### Error: "No se obtuvo el token de aceptación"
- Verifica que `WOMPI_PUBLIC_KEY` sea correcto
- Comprueba la conexión a internet
- En sandbox, usa URLs de `sandbox.wompi.co`

### Webhook no se ejecuta
- Verifica que el webhook esté configurado en dashboard de Wompi
- Comprueba que la URL sea accesible públicamente
- Revisa los logs de Wompi para errores

### Pedidos se quedan en "Pendiente"
- Asegúrate de que el webhook está procesando eventos
- Verifica que `wompi_reference` sea único
- Revisa la consola Django para errores en `wompi_webhook`

## Seguridad

✅ **Implementado:**
- Validación de usuario propietario del pedido
- Verificación de estado antes de permitir pago
- Token de aceptación de Wompi para transacciones
- Webhook con validación de referencia

⚠️ **Recomendaciones Adicionales:**
- En producción, verifica la firma del webhook si Wompi la proporciona
- Usa HTTPS obligatoriamente
- Implementa rate limiting en endpoints de pago
- Registra todas las transacciones para auditoría

## API Reference

### Vista: `pagar_pedido(request, pedido_id)`
```python
# GET o POST a /pedidos/<id>/pagar/
# Redirige a Wompi o muestra error
```

### Vista: `wompi_retorno(request)`
```python
# GET a /pagos/wompi/retorno/
# Página de confirmación post-pago
```

### Vista: `wompi_webhook(request)`
```python
# POST a /pagos/wompi/webhook/
# Procesa eventos de Wompi
# Responde con 200 OK si es válido
```

## Próximas Mejoras
- [ ] Validación de firma HMAC del webhook
- [ ] Soporte para múltiples métodos de pago
- [ ] Reintentos automáticos de pago fallido
- [ ] Reportes de pagos por período
- [ ] Notificaciones por email de pagos

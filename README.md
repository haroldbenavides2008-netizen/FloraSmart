FloraSmart 


Es una plataforma web integral diseñada para optimizar la comercialización de flores, permitiendo a los floricultores gestionar sus cultivos y a los compradores adquirir productos frescos directamente, sin intermediarios.

Características Principales
Mercado Digital: Catálogo de flores con filtros avanzados por nombre, categoría y colores.

Gestión de Inventario: Panel exclusivo para floricultores donde pueden agregar, editar y eliminar sus productos.

Sistema de Pedidos: Proceso de compra simplificado con historial de pedidos para clientes y productores.

Chat en Tiempo Real: Comunicación directa integrada con Firebase para negociaciones rápidas.

Autenticación Segura: Sistema de registro y login diferenciado por roles (Comprador/Floricultor).

Panel Administrativo: Control total de la base de datos mediante el administrador de Django.

Tecnologías Utilizadas
Backend: Python 3.x & Django 5.x.

Base de Datos:  Firebase Realtime Database (Chat).

Frontend: HTML5, CSS3 (Flexbox/Grid) .

Autenticación: Django Auth & Firebase Admin SDK.

Estilos: Diseño personalizado con enfoque en experiencia de usuario (UX).

 Instalación y Configuración
Sigue estos pasos para ejecutar el proyecto localmente:

Clonar el repositorio:

Bash
git clone https://github.com/tu-usuario/FloraSmart.git
cd FloraSmart
Crear y activar el entorno virtual:

Bash
python -m venv venv
# En Windows:
.\venv\Scripts\activate
Instalar dependencias:

Bash
pip install django firebase-admin
Realizar migraciones:

Bash
python manage.py makemigrations
python manage.py migrate
Crear un superusuario (Admin):

Bash
python manage.py createsuperuser
Iniciar el servidor:

Bash
python manage.py runserver
 Vista Previa del Proyecto
(Aquí puedes añadir las rutas de las imágenes que me has mostrado)

Mercado de Flores: Interfaz limpia con tarjetas de productos y sistema de filtrado dinámico.

Gestión de Pedidos: Tabla organizada con estados de pedido ("Solicitado", "Enviado", etc.).

Chat: Interfaz estilo mensajería moderna para soporte y ventas.

Autores
Desarrollado por: Harold Benavides y Maria Mosquera

Programa: Análisis y Desarrollo de Software 

FloraSmart 🌸
Gestión de inventario y comercio sostenible para la floricultura.

- Descripción
FloraSmart es una plataforma digital desarrollada para resolver el desperdicio en la industria floricultora. El proyecto se centra en la comercialización de flores de segunda mano: productos que, aunque no cumplen con los estrictos estándares de exportación, mantienen una calidad estética óptima para el mercado local.

El sistema permite a los floricultores gestionar su inventario de excedentes y a los compradores acceder a productos de alta calidad a precios justos, fomentando la sostenibilidad y la economía circular.

- Integrantes
Maria Isabel Mosquera Reyes 
Harold Benavides 

- Tecnologías utilizadas
Lenguaje: Python 3.12+

Framework: Django 5.0

Base de datos: SQLite (Arquitectura local centralizada)

Entorno: WSL 2 (Ubuntu) / Docker Desktop

Estilos: CSS3 personalizado 

- Requisitos previos
Para ejecutar este proyecto, asegúrate de tener instalado:

Python 3.10 o superior.

Git.

WSL 2 configurado (si trabajas en Windows).

- Instalación y Configuración
Sigue estos pasos para preparar tu entorno de desarrollo:

-Clonar el repositorio:
Bash
git clone https://github.com/TuUsuario/FloraSmart.git
cd FloraSmart

-Crear el entorno virtual:
Bash
python -m venv venv

-Activar el entorno virtual:
En Windows: .\venv\Scripts\activate

Instalar dependencias:

Bash
pip install -r requirements.txt
-Ejecución Local (Orden de Comandos)
Para asegurar que la base de datos esté limpia y reconozca el nuevo sistema de usuarios (sin dependencias externas), ejecuta los comandos en este orden:

-Preparar las migraciones del modelo de Usuario:
Bash
python manage.py makemigrations usuarios

-Aplicar las migraciones a la base de datos:
Bash
python manage.py migrate

-Iniciar el servidor de desarrollo:
Bash
python manage.py runserver
Accede al sistema en: http://127.0.0.1:8000/

🗄️ Base de datos y Arquitectura
El proyecto utiliza exclusivamente la base de datos interna de Django (SQLite). Se ha eliminado la integración con Firebase para centralizar la lógica de autenticación, roles (Floricultor/Cliente) y gestión de pedidos en un solo lugar, garantizando rapidez y estabilidad en el desarrollo local.


Roles: El sistema permite registrarse como Floricultor (para subir productos) o como Cliente (para realizar pedidos).

import os
import firebase_admin
from firebase_admin import credentials
from pathlib import Path

# 1. Rutas base del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent

# 2. Seguridad (Mantén estas claves seguras en producción)
SECRET_KEY = 'django-insecure-01m1b+8n@y3119_e@qxi2+eryn3#gb9v^@a7%^(w3*6p3#=uct'
DEBUG = True
ALLOWED_HOSTS = []

# 3. Aplicaciones Instaladas
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Herramientas para FloraSmart
    'rest_framework',
    'corsheaders',
    'usuarios', # Tu aplicación de gestión de usuarios
]

# 4. Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware', # Recomendado añadirlo aquí
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

# 5. Configuración de Plantillas (HTML)
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'], # Ruta corregida para buscar tus HTML
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

# 6. Base de Datos Local (SQLite)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# 7. Internacionalización
LANGUAGE_CODE = 'es-co' # Cambiado a español de Colombia
TIME_ZONE = 'America/Bogota'
USE_I18N = True
USE_TZ = True

# 8. Archivos Estáticos (CSS, JS)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles' # Para producción
STATICFILES_DIRS = [
    BASE_DIR / 'static', # Carpeta principal de estáticos en la raíz
]

# 9. Archivos Multimedia (Fotos de las flores y fincas)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# 10. Configuración de CORS (Para desarrollo)
CORS_ALLOW_ALL_ORIGINS = True
AUTH_USER_MODEL = 'usuarios.Usuario'
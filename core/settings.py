import os
import firebase_admin
from firebase_admin import credentials
from pathlib import Path
import dj_database_url

# 1. Rutas base del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent

# Carga de variables de entorno desde .env cuando exista
dotenv_path = BASE_DIR / '.env'
if dotenv_path.exists():
    with open(dotenv_path, encoding='utf-8') as dotenv_file:
        for line in dotenv_file:
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            key, value = line.split('=', 1)
            os.environ.setdefault(key.strip(), value.strip())

# 2. Seguridad
SECRET_KEY = os.getenv(
    'SECRET_KEY',
    'django-insecure-01m1b+8n@y3119_e@qxi2+eryn3#gb9v^@a7%^(w3*6p3#=uct'
)

DEBUG = os.getenv('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = [
    '.onrender.com',
    'localhost',
    '127.0.0.1',
]

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
    'cloudinary',
    'cloudinary_storage',
    'usuarios',
]

# 4. Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

# 5. Configuración de Plantillas
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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
# 6. Base de Datos

if os.getenv("DATABASE_URL"):
    DATABASES = {
        'default': dj_database_url.parse(
            os.getenv("DATABASE_URL"),
            conn_max_age=600,
            ssl_require=True
        )
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# 7. Validadores de Contraseña
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# 8. Internacionalización
LANGUAGE_CODE = 'es-co'
TIME_ZONE = 'America/Bogota'

USE_I18N = True
USE_TZ = True

# 9. Archivos Estáticos
STATIC_URL = '/static/'

STATIC_ROOT = BASE_DIR / 'staticfiles'

STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

# 10. Archivos Multimedia
# 10. Archivos Multimedia

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.getenv('CLOUDINARY_CLOUD_NAME'),
    'API_KEY': os.getenv('CLOUDINARY_API_KEY'),
    'API_SECRET': os.getenv('CLOUDINARY_API_SECRET'),
}

USE_CLOUDINARY = all(CLOUDINARY_STORAGE.values())

if USE_CLOUDINARY:
    import cloudinary

    cloudinary.config(
        cloud_name=CLOUDINARY_STORAGE['CLOUD_NAME'],
        api_key=CLOUDINARY_STORAGE['API_KEY'],
        api_secret=CLOUDINARY_STORAGE['API_SECRET'],
    )

    STORAGES = {
        "default": {
            "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
        },
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
        },
    }

else:
    STORAGES = {
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
        },
    }
# 11. Configuración de CORS
CORS_ALLOW_ALL_ORIGINS = True

# 12. Usuario Personalizado
AUTH_USER_MODEL = 'usuarios.Usuario'

# 13. Configuración de Wompi
WOMPI_PUBLIC_KEY = os.getenv(
    'WOMPI_PUBLIC_KEY',
    'your_public_key_here'
)

WOMPI_PRIVATE_KEY = os.getenv(
    'WOMPI_PRIVATE_KEY',
    'your_private_key_here'
)

WOMPI_REDIRECT_URL = os.getenv(
    'WOMPI_REDIRECT_URL',
    'http://localhost:8000/pagos/wompi/retorno/'
)

WOMPI_WEBHOOK_URL = os.getenv(
    'WOMPI_WEBHOOK_URL',
    'http://localhost:8000/pagos/wompi/webhook/'
)

WOMPI_SANDBOX_URL = 'https://sandbox.wompi.co'

# 14. Firebase (solo si existe configuración)
firebase_cred_path = os.getenv('FIREBASE_CREDENTIALS')

if firebase_cred_path and os.path.exists(firebase_cred_path):
    if not firebase_admin._apps:
        cred = credentials.Certificate(firebase_cred_path)
        firebase_admin.initialize_app(cred)

# 15. Campo automático por defecto
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
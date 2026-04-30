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
from django.contrib import admin
from django.urls import path
from usuarios import views  # Importamos todo el módulo de vistas para mayor orden

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Rutas de Autenticación
    path('', views.login_view, name='login'),
    path('registro/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    # Rutas de la Aplicación (Dashboard de FloraSmart)
    path('home/', views.home_view, name='home'),
    path('agregar-producto/', views.agregar_producto, name='agregar_producto'),
]
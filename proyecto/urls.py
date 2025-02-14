"""
URL configuration for proyecto project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.urls import path, include
from rest_framework import routers
from app.views import ReporteViewSet, MedidasViewSet, OrganismoSectorialViewSet, UsuarioViewSet

#from DRF-spectacular (documentation)
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

router = routers.DefaultRouter()


router.register(r'usuarios', UsuarioViewSet)
router.register(r'organismossectoriales', OrganismoSectorialViewSet)
router.register(r'medidas', MedidasViewSet)
router.register(r'reportes', ReporteViewSet, basename='reporte')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls')),     #permite loguear y desloguear de DRF en la version web

    #SCHEMA DRF-Spectacular
    # Generador de Schema-file
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    # Interfaz opcionales para documentación:
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
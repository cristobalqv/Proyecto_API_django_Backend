from django.core.files.uploadedfile import SimpleUploadedFile
from app.models import OrganismoSectorial, Usuario, Medidas
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import Permission
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

class ReporteAPITest(APITestCase):

    def setUp(self):

        # Crear organismo
        #En este test se crea primero el organismo, ya que el usuario es fiscalizador y no un superuser
        self.organismo = OrganismoSectorial.objects.create(
            tipo_ente='Superintendencia',
            codigo_ente='SEC005',
            region='Los Rios'
        )

        # Crear usuario fiszalizador y autenticarse
        self.user = User.objects.create_user(
            username='fiscalizador_test',
            password='pass1234',
            organismo_sectorial=self.organismo,
            autorizado_para_reportes=True
            #is_staff=True, -- Para esta prueba no es superuser
            #is_superuser=True
        )

        # Asignar permiso explicito para crear reportes
        permiso_add_reporte = Permission.objects.get(codename='add_reporte')
        self.user.user_permissions.add(permiso_add_reporte)

        refresh = RefreshToken.for_user(self.user)
        self.token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
 
        #Crear Medida
        self.medida = Medidas.objects.create(
            nombre="Control de emisiones",
            descripcion="Control anual",
            extension_permitida=".pdf",
            obligatorio=True
        )
        self.medida.organismos_permitidos.add(self.organismo)

        self.client.force_authenticate(user=self.user)

    # Test 1: Subir reporte validado
    def test_subir_reporte_valido(self):
        archivo = SimpleUploadedFile("test.pdf", b"contenido del archivo", content_type="application/pdf")
        response = self.client.post('/api/reportes/', {
            "tipo_medida": self.medida.id,
            "archivo": archivo,
            "usuario": self.user.id  # revisar pq no se asigna automaticamente
        }, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    #Test 2: Subir un reporte que no esta permitido para el usuario
    def test_subir_reporte_no_permitido(self):
        otro_organismo = OrganismoSectorial.objects.create(
            tipo_ente='Otro',
            codigo_ente='XYZ001',
            region='Tarapacá'
        )
        self.user.organismo_sectorial = otro_organismo
        self.user.save()

        archivo = SimpleUploadedFile("test.pdf", b"contenido del archivo", content_type="application/pdf")
        response = self.client.post('/api/reportes/', {
            "tipo_medida": self.medida.id,
            "archivo": archivo
        }, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    #Test para listar, detallar, actualizar y borrar
    def test_listar_reportes(self):
        response = self.client.get('/api/reportes/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_detalle_reporte(self):
        # Crear un reporte válido primero
        archivo = SimpleUploadedFile("test.pdf", b"contenido del archivo", content_type="application/pdf")
        post_response = self.client.post('/api/reportes/', {
            "tipo_medida": self.medida.id,
            "archivo": archivo,
            "usuario": self.user.id
        }, format='multipart')
        reporte_id = post_response.data["id"]

        # Obtener el detalle del reporte
        response = self.client.get(f'/api/reportes/{reporte_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    #Este test es importante ya que el usuario fiscalizador no puede borrar reportes que ya envio
    def test_borrar_reporte_no_autorizado(self):
        archivo = SimpleUploadedFile("test.pdf", b"contenido del archivo", content_type="application/pdf")
        post_response = self.client.post('/api/reportes/', {
            "tipo_medida": self.medida.id,
            "archivo": archivo,
            "usuario": self.user.id
        }, format='multipart')
        reporte_id = post_response.data["id"]

        # El usuario fiscalizador NO debería poder borrar
        response = self.client.delete(f'/api/reportes/{reporte_id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


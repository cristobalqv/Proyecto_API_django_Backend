from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from app.models import OrganismoSectorial

User = get_user_model()

class OrganismoSectorialAPITest(APITestCase):

    def setUp(self):
        # Crear usuario admin autenticado
        self.user = User.objects.create_user(
            username='admin_test',
            password='pass1234',
            is_staff=True,
            is_superuser=True
        )
        refresh = RefreshToken.for_user(self.user)
        self.token = str(refresh.access_token)

        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

        # Crear un organismo
        self.organismo = OrganismoSectorial.objects.create(
            tipo_ente='Superintendencia',
            codigo_ente='SEC001',
            region='Metropolitana'
        )

    def test_listar_organismos(self):
        response = self.client.get('/api/organismossectoriales/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_crear_organismo(self):
        data = {
            "tipo_ente": "Seremi",
            "codigo_ente": "SER001",
            "region": "Valparaíso"
        }
        response = self.client.post('/api/organismossectoriales/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_detalle_organismo(self):
        response = self.client.get(f'/api/organismossectoriales/{self.organismo.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_actualizar_organismo(self):
        data = {
            "tipo_ente": "Superintendencia Actualizada",
            "codigo_ente": "SEC001",
            "region": "Biobío"
        }
        response = self.client.put(f'/api/organismossectoriales/{self.organismo.id}/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_actualizacion_parcial_organismo(self):
        data = {
            "region": "Coquimbo"
        }
        response = self.client.patch(f'/api/organismossectoriales/{self.organismo.id}/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_borrar_organismo(self):
        response = self.client.delete(f'/api/organismossectoriales/{self.organismo.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
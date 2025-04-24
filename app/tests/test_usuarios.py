from django.contrib.auth import get_user_model
from app.models import OrganismoSectorial
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

class UsuarioAPITest(APITestCase):

    def setUp(self):
        # Crear usuario admin y autenticarse
        self.user = User.objects.create_user(
            username='admin_test',
            password='pass1234',
            is_staff=True,
            is_superuser=True
        )
        refresh = RefreshToken.for_user(self.user)
        self.token = str(refresh.access_token)

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        
        #Crear Organismo
        self.organismo = OrganismoSectorial.objects.create(
            tipo_ente='Superintendencia',
            codigo_ente='SEC004',
            region='Biobío'
    )
    # Test 1: Crear un usuario fiscalizador autorizado    
    def test_crear_usuario_autorizado(self):
        data = {
            "username": "fiscalizador",
            "password": "test1234",
            "first_name": "Rodrigo",
            "last_name": "Araya",
            "email": "raraya@test.cl",
            "autorizado_para_reportes": True,
            "organismo_sectorial": self.organismo.id
        }
        response = self.client.post('/api/usuarios/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    #Test 2: Crear un usuario pero sin autorizacion para reportes
    def test_crear_usuario_sin_autorizacion(self):
        data = {
            "username": "noautorizado",
            "password": "test1234",
            "autorizado_para_reportes": False,
            "organismo_sectorial": self.organismo.id
        }
        response = self.client.post('/api/usuarios/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    #Test para listar, detallar, actualizar y borrar
    def test_listar_usuarios(self):
        response = self.client.get('/api/usuarios/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_detalle_usuario(self):
        response = self.client.get(f'/api/usuarios/{self.user.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_actualizar_usuario(self):
        data = {
            "username": "actualizacion_username",
            "password": "pass1234_actualizada", 
            "first_name": "Rodrigo",
            "last_name": "Aaraya",
            "email": "admin@test.cl",
            "organismo_sectorial": self.organismo.id,
            "autorizado_para_reportes": True
        }
        response = self.client.put(f'/api/usuarios/{self.user.id}/', data, format='json')
        print("RESPONSE STATUS:", response.status_code)
        print("RESPONSE DATA:", response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def test_actualizacion_parcial_usuario(self):
        data = {
            "first_name": "RodrigoActualizado"
        }
        response = self.client.patch(f'/api/usuarios/{self.user.id}/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_borrar_usuario(self):
        response = self.client.delete(f'/api/usuarios/{self.user.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
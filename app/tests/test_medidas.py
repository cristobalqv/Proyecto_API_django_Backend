from app.models import Medidas, OrganismoSectorial
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status

from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

class MedidasAPITest(APITestCase):

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
            region='Valparaiso'
    )

    #Test 1: Crear medida
    def test_crear_medida(self):
        response = self.client.post('/api/medidas/', {
            "nombre": "Informe de emisiones",
            "descripcion": "Medida anual de emisiones",
            "extension_permitida": ".pdf",
            "obligatorio": True,
            "organismos_permitidos": [self.organismo.id]
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #Test 2: No hay nombre de medidas duplicados
    def test_nombre_unico_medida(self):
        Medidas.objects.create(
            nombre="Informe de emisiones",
            descripcion="Uno",
            extension_permitida=".pdf",
            obligatorio=False
        )
        response = self.client.post('/api/medidas/', {
            "nombre": "Informe de emisiones",  # mismo nombre
            "descripcion": "Dos",
            "extension_permitida": ".doc",
            "obligatorio": False
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    #Test para listar, detallar, actualizar y borrar
    def test_listar_medidas(self):
        response = self.client.get('/api/medidas/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_detalle_medida(self):
        medida = Medidas.objects.create(
            nombre="Medida Detalle",
            descripcion="Descripción prueba",
            extension_permitida=".pdf",
            obligatorio=False
        )
        response = self.client.get(f'/api/medidas/{medida.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_actualizar_medida(self):
        medida = Medidas.objects.create(
            nombre="Temporal",
            descripcion="Old",
            extension_permitida=".doc",
            obligatorio=False
        )
        data = {
            "nombre": "Actualizado",
            "descripcion": "Descripción actualizada",
            "extension_permitida": ".pdf",
            "obligatorio": True,
            "organismos_permitidos": [self.organismo.id]
        }
        response = self.client.put(f'/api/medidas/{medida.id}/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_borrar_medida(self):
        medida = Medidas.objects.create(
            nombre="Eliminar",
            descripcion="Eliminar esta medida",
            extension_permitida=".pdf",
            obligatorio=True
        )
        response = self.client.delete(f'/api/medidas/{medida.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

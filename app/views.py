# Create your views here.

from django.shortcuts import render

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions, IsAdminUser
from app.api.serializers import ReporteSerializer, MedidasSerializer, OrganismoSectorialSerializer, UsuarioSerializer
from app.models import Usuario, Reporte, Medidas, OrganismoSectorial
from django.contrib.auth.models import Group, Permission
from .permissions import PuedeRevisarReportes
# Create your views here.

class UsuarioViewSet(viewsets.ModelViewSet):
    serializer_class = UsuarioSerializer
    queryset = Usuario.objects.all()
    permission_classes = [IsAdminUser]



class OrganismoSectorialViewSet(viewsets.ModelViewSet):
    serializer_class = OrganismoSectorialSerializer
    queryset = OrganismoSectorial.objects.all()
    permission_classes = [IsAdminUser]



class MedidasViewSet(viewsets.ModelViewSet):
    serializer_class = MedidasSerializer
    queryset = Medidas.objects.all()
    permission_classes = [IsAuthenticated]


    def get_queryset(self):
        '''filtramos las medidas para que los usuarios vean solo
        las correspondientes a su organismo sectorial'''
        user = self.request.user

        if user.has_perm('app.can_view_all_measures'):
            return Medidas.objects.filter(organismos_permitidos = user.organismo_sectorial)   
        return Medidas.objects.none()



class ReporteViewSet(viewsets.ModelViewSet):
    serializer_class = ReporteSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]

    queryset = Reporte.objects.all()

    def get_queryset(self):
        """
        Filtramos los reportes para que cada usuario solo vea los suyos,
        excepto si tiene permisos especiales
        """
        user = self.request.user

        if user.has_perm('app.can_view_all_reports'):
            return Reporte.objects.all()
        return Reporte.objects.filter(usuario=user)
    
    def get_tipos_documentos_permitidos(self):
        """
        Retorna las medidas para el tipo de ente del usuario actual
        """
        return Medidas.objects.filter(
            tipo_ente=self.request.user.organismos_permitidos
        )
    

    @action(detail=True, methods=['patch'], permission_classes=[PuedeRevisarReportes])
    def revisar(self, request, pk=None):
        """
        Permite a usuarios con permiso revisar y cambiar el estado del reporte.
        """
        reporte = self.get_object()
        nuevo_estado = request.data.get('estado')

        if nuevo_estado not in ['APROBADO', 'RECHAZADO']:
            return Response({'error': 'Estado inválido. Solo puede ser APROBADO o RECHAZADO.'},
                            status=status.HTTP_400_BAD_REQUEST)

        reporte.estado = nuevo_estado
        reporte.save()

        return Response({
            'mensaje': f'Reporte actualizado a {nuevo_estado}.',
            'reporte_id': reporte.id
            }, status=status.HTTP_200_OK)

#crearemos un grupo "fiscalizadores" con permisos especiales
class GrupoViewSet(viewsets.ViewSet):
    permission_classes = [IsAdminUser]  # Protege todas las acciones del ViewSet

    @action(detail=False, methods=['post'], url_path='crear-fiscalizadores')
    def crear_grupo_fiscalizadores(self, request):
        grupo, creado = Group.objects.get_or_create(name='Fiscalizadores')

        permisos_deseados = [
            'view_reporte',
            'add_organismosectorial', 'change_organismosectorial', 'view_organismosectorial',
            'add_medidas', 'view_medidas',
        ]

        permisos = Permission.objects.filter(codename__in=permisos_deseados)
        grupo.permissions.set(permisos)
        grupo.save()

        return Response({
            'grupo': grupo.name,
            'creado': creado,
            'permisos_asignados': [perm.codename for perm in permisos]
        }, status=status.HTTP_200_OK)
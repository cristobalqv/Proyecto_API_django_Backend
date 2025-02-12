from django.shortcuts import render

# Create your views here.

from django.shortcuts import render

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions, IsAdminUser
from app.api.serializers import DocumentoSerializer, TipoDocumentoPermitidoSerializer, OrganismoSectorialSerializer
from app.models import Usuario, Documento, TipoDocumentoPermitido, OrganismoSectorial
# Create your views here.


class TipoDocumentoPermitidoViewSet(viewsets.ModelViewSet):
    serializer_class = TipoDocumentoPermitidoSerializer
    queryset = TipoDocumentoPermitido.objects.all()
    permission_classes = [IsAdminUser]



class DocumentoViewSet(viewsets.ModelViewSet):
    serializer_class = DocumentoSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]

    queryset = Documento.objects.all()

    def get_queryset(self):
        """
        Filtramos los documentos para que cada usuario solo vea los suyos,
        excepto si tiene permisos especiales
        """
        user = self.request.user

        if user.has_perm('app.can_view_all_documents'):
            return Documento.objects.all()
        return Documento.objects.filter(usuario=user)
    
    def get_tipos_documentos_permitidos(self):
        """
        Retorna los tipos de documentos permitidos para el tipo de ente del usuario actual
        """
        return TipoDocumentoPermitido.objects.filter(
            tipo_ente=self.request.user.tipo_ente
        )
    

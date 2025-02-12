from django.db import models

# Create your models here.

from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db.models import UniqueConstraint
from app.api.validators import custom_validate_file
from django.core.exceptions import ValidationError

# Create your models here.


class OrganismoSectorial(models.Model):
    """Modelo que representa cada organismo sectorial"""

    tipo_ente = models.CharField(
        max_length=100,
        #choices = TIPOS_ENTE,
        verbose_name = 'Tipo de ente fiscalizador'
    )

    codigo_ente = models.CharField(
        max_length=20,
        unique = True,
        verbose_name = 'Código del ente'
    )

    region = models.CharField(
        max_length=100,
        verbose_name='Region',
        blank=True
    )

    def __str__(self):
        return f"{self.tipo_ente} - {self.codigo_ente}"     #Metodo especial creado por django automaticamente al definir un campo con "choices". Permite acceder al dato "amigable"

    # def clean(self):
    #     if self.tipo_ente in ['servicio_evaluacion_ambiental', 'intendencia_regional_valparaiso'] and not self.region:
    #         raise ValidationError({
    #             'region': "La región es obligatoria para este tipo de organismo"
    #         })


class Usuario(AbstractUser):
    """
    Modelo de Usuario personalizado que representa un usuario de un organismo sectorial (fiscalizador).
    Hereda todas las funcionalidades básicas de usuario de Django y añade campos específicos.
    """

    organismo_sectorial = models.ForeignKey(
        OrganismoSectorial, on_delete=models.CASCADE, 
        related_name='usuarios',
        null=True,
        blank=True
        )

    autorizado_para_reportes = models.BooleanField(default=False)

    # Redefinimos estas relaciones explícitamente
    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        related_name='custom_user_set'
    )

    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        related_name='custom_user_set'
    )


    class Meta:
        permissions = [
            ("can_upload_documents", "Puede subir documentos"),
            ("can_view_all_documents", "Puede ver todos los documentos"),
        ]

    

def documento_upload_path(instance, filename):
    #Generamos una ruta personalizada basada en el usuario (ente fiscalizador) y el tipo de documento
    return f"documentos/{instance.usuario.organismo_sectorial.codigo_ente}/{instance.tipo_documento.nombre}/{filename}"
   


class Documento(models.Model):     #clase que representa cada archivo que se sube al sistema
    """
    Modelo para manejar los documentos subidos por los entes fiscalizadores.
    Cada documento está asociado directamente con el usuario que lo subió.
    """
    usuario = models.ForeignKey(     #usuario que sube el archivo
        Usuario, 
        on_delete=models.CASCADE, 
        related_name='documentos'
        )
    
    tipo_documento = models.ForeignKey(     
        'TipoDocumentoPermitido',
        on_delete=models.CASCADE,
        )

    archivo = models.FileField(     #que archivo es
        upload_to=documento_upload_path,
        # validators=['custom_validate_file']     #Funcion validadora a crear. Corchetes ya que validators espera una lista de funciones validadoras (pueden ser varias)
        )

    fecha_subida=models.DateTimeField(auto_now_add=True)

    estado=models.CharField(
        max_length=20,
        choices=[
            ('PENDIENTE', 'Pendiente de revisión'),     #
            ('APROBADO', 'aprobado'),
            ('RECHAZADO', 'rechazado')
        ],
        default='PENDIENTE'
    )

    def clean(self):     #metodo para validar datos de un formulario
        # Validar que el usuario pertenezca a un organismo que puede subir este tipo de documento
        if not self.tipo_documento.organismos_permitidos.filter(id=self.usuario.organismo_sectorial.id).exists():
            raise ValidationError({
                'tipo_documento': "Este tipo de documento no está permitido para su organismo sectorial."
            })
        
        # Validar que el usuario esté autorizado para subir reportes
        if not self.usuario.autorizado_para_reportes:
            raise ValidationError({
                'usuario': "Este usuario no está autorizado para subir documentos."
            })

    def save(self, *args, **kwargs):
        self.clean()  # Llamar a la validación antes de guardar
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.usuario.organismo_sectorial.tipo_ente} - {self.tipo_documento.nombre}"
    


class TipoDocumentoPermitido(models.Model):     #define la configuracion del documento que puede subir cada usuario. No confundir con extensión de documento
    """
    Se define qué tipos de documentos pueden subir cada usuario.
    """

    nombre = models.CharField(max_length=100)     #documento específico que puede subir cada organismo. Ejemplo: "Catastro de incendios forestales"
    descripcion = models.TextField(blank=True)
    extension_permitida = models.CharField(max_length=10)

    obligatorio = models.BooleanField(
        default=False,
        help_text="Indica si este documento es de entrega obligatoria"
    )

    #cada tipo de documento puede asociarse a multiples usuarios
    organismos_permitidos = models.ManyToManyField(
        OrganismoSectorial,
        related_name='tipos_documentos_permitidos'
    )     #permite asociar varios usuarios a un mismo documento 
    

    class Meta:
        constraints = [
            UniqueConstraint(fields=['nombre'], name='unique_tipo_documento')     #UniqueConstraint impone restricciones de unicidad
            #en uno o mas campos de la base de datos evitando que se repitan En este caso, no peuden haber 2 tipos de documentos con el mismo nombre. 
            #Campo "nombre" debe ser unico en la tabla
        ]     


    def save(self, *args, **kwargs):
        print(f"Guardando TipoDocumentoPermitido: {self.nombre}")  
        super().save(*args, **kwargs)
        print(f"Guardado exitosamente: {self.nombre}")


    def __str__(self):
        organismos = ", ".join([org.codigo_ente for org in self.organismos_permitidos.all()])
        return f"{self.nombre} - Permitido para: {organismos}"
    


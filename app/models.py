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
        return f"{self.tipo_ente} - {self.codigo_ente}"     
    


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
            ("can_upload_reports", "Puede subir reportes"),
            ("can_view_all_reports", "Puede ver todos los reportes"),
            ("can_view_all_measures", "Puede ver todas las medidas"),
            ("can_review_reports", "Puede revisar (aprobar/rechazar) reportes"),

        ]

    

def reporte_upload_path(instance, filename):
    #Generamos una ruta personalizada basada en el usuario (ente fiscalizador) y la medida
    return f"reportes/{instance.usuario.organismo_sectorial.codigo_ente}/{instance.tipo_medida.nombre}/{filename}"



class Reporte(models.Model):     #clase que representa cada archivo que se sube al sistema
    """
    Modelo para manejar los reportes subidos por los usuarios asociados a un organismo sectorial.
    Cada reporte está asociado directamente con el usuario que lo subió.
    """
    usuario = models.ForeignKey(     #usuario que sube el archivo
        Usuario, 
        on_delete=models.CASCADE, 
        related_name='reportes'
        )
    
    tipo_medida = models.ForeignKey(     
        'Medidas',
        on_delete=models.CASCADE,
        )

    archivo = models.FileField(     
        upload_to= reporte_upload_path,
        # validators=['custom_validate_file']     
        )
    '''custom_validate_file = Funcion validadora. Corchetes ya que validators 
    espera una lista de funciones validadoras (pueden ser varias y personalizables)'''

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
        # Validar que el usuario pertenezca a un organismo que puede subir este tipo de medida
        if not self.tipo_medida.organismos_permitidos.filter(id=self.usuario.organismo_sectorial.id).exists():
            raise ValidationError({
                'tipo_medida': "Esta medida no está permitido para su organismo sectorial."
            })
        
        # Validar que el usuario esté autorizado para subir reportes
        if not self.usuario.autorizado_para_reportes:
            raise ValidationError({
                'usuario': "Este usuario no está autorizado para generar reportes."
            })

    def save(self, *args, **kwargs):
        self.clean()  # Llamar a la validación antes de guardar
        super().save(*args, **kwargs)




        # ## ESTO ES NUEVO

        # class Meta:
        #     permissions = [
        #         ("can_review_reports", "Puede revisar (aprobar/rechazar) reportes"),
        #     ]

        # ##ESTO ES NUEVO




    def __str__(self):
        return f"{self.usuario.organismo_sectorial.tipo_ente} - {self.tipo_medida.nombre}"
    


class Medidas(models.Model):     
    """
    Se define a que Medidas debe dar cuenta cada usuario de org sectorial. Pueden tener formatos compartidos o propios.
    Ejemplo: "Control emisiones complejo termoelectrico ventanas" solo lo sube Superintendencia electricidad y combustibles
    """

    nombre = models.CharField(max_length=100)    
    descripcion = models.TextField(blank=True)
    extension_permitida = models.CharField(max_length=10)

    obligatorio = models.BooleanField(
        default=False,
        help_text="Indica si esta medida es de entrega obligatoria"
    )

    #cada medida puede ser reportada por multiples usuarios
    organismos_permitidos = models.ManyToManyField(
        OrganismoSectorial,
        related_name='medidas_permitidas'
    )    
    

    class Meta:
        constraints = [
            UniqueConstraint(fields=['nombre'], name='unique_tipo_medida')   
        ]     
        '''UniqueConstraint impone restricciones de unicidad en uno o mas campos 
        de la base de datos evitando que se repitan. En este caso, no pueden haber 
        2 tipos de medidas con el mismo nombre. Campo "nombre" debe ser unico en la tabla'''


    def save(self, *args, **kwargs):
        print(f"Guardando Medida: {self.nombre}")  
        super().save(*args, **kwargs)
        print(f"Guardado exitosamente: {self.nombre}")


    def __str__(self):
        organismos = ", ".join([org.codigo_ente for org in self.organismos_permitidos.all()])
        return f"{self.nombre} - Permitido para: {organismos}"
    
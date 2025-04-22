from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db.models import UniqueConstraint
from app.api.validators import custom_validate_file
from django.core.exceptions import ValidationError

# Create your models here.


class OrganismoSectorial(models.Model):
    """
    Modelo que representa un organismo sectorial.

    Atributos:
        tipo_ente (str): Tipo de ente fiscalizador.
        codigo_ente (str): Código único del ente.
        region (str): Región asociada (opcional).
    """
    tipo_ente = models.CharField(
        max_length=100,
        verbose_name='Tipo de ente fiscalizador'
    )

    codigo_ente = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='Código del ente',
    )

    region = models.CharField(
        max_length=100,
        verbose_name='Region',
        blank=True,
    )

    def __str__(self):
        return f"{self.tipo_ente} - {self.codigo_ente}"     
    


class Usuario(AbstractUser):
    """
        Modelo de usuario personalizado que extiende AbstractUser.

        Este modelo representa usuarios pertenecientes a organismos sectoriales.
        Además de los campos estándar de Django, incorpora:
        - Una relación con el modelo OrganismoSectorial.
        - Un flag booleano para determinar autorización para reportes.
        - Redefinición explícita de grupos y permisos con related_name personalizado.
    """

    organismo_sectorial = models.ForeignKey(
        OrganismoSectorial, 
        on_delete=models.CASCADE, 
        related_name='usuarios',
        null=True,
        blank=True
    )

    autorizado_para_reportes = models.BooleanField(
        default=False,
        help_text="Indica si el usuario tiene autorización para acceder al módulo de reportes"
    )

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
        """
            Permisos personalizados para el modelo Usuario.
            Se utilizan para controlar el acceso a funcionalidades específicas del sistema.
        """
        permissions = [
            ("can_upload_reports", "Puede subir reportes"),
            ("can_view_all_reports", "Puede ver todos los reportes"),
            ("can_view_all_measures", "Puede ver todas las medidas"),
            ("can_review_reports", "Puede revisar (aprobar/rechazar) reportes")
        ]

    

def reporte_upload_path(instance, filename):
    #Generamos una ruta personalizada basada en el usuario (ente fiscalizador) y la medida
    return f"reportes/{instance.usuario.organismo_sectorial.codigo_ente}/{instance.tipo_medida.nombre}/{filename}"



class Reporte(models.Model):     #clase que representa cada archivo que se sube al sistema
    """
    Modelo para manejar los reportes subidos por los usuarios asociados a un organismo sectorial.

    Atributos:
        usuario (Usuario): Usuario que sube el archivo, asociado a un organismo sectorial.
        tipo_medida (Medidas): Tipo de medida asociada al reporte.
        archivo (FileField): Archivo subido por el usuario.
        fecha_subida (DateTime): Fecha en que se subió el archivo.
        estado (CharField): Estado del reporte (pendiente, aprobado o rechazado).
    """

    usuario = models.ForeignKey(
        Usuario, 
        on_delete=models.CASCADE, 
        related_name='reportes',
        help_text="Usuario que sube el archivo."
    )
    
    tipo_medida = models.ForeignKey(
        'Medidas',
        on_delete=models.CASCADE,
        help_text="Medida asociada al reporte"
    )

    """
    Por Validar: 
    custom_validate_file = Funcion validadora. Corchetes ya que validators 
    espera una lista de funciones validadoras (pueden ser varias y personalizables)
    """
    archivo = models.FileField(
        upload_to= reporte_upload_path,
        # validators=['custom_validate_file'],
        help_text="Archivo del reporte a subir"     
    )
    
    fecha_subida=models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha en que se sube el archivo",
    )

    estado=models.CharField(
        max_length=20,
        choices=[
            ('PENDIENTE', 'Pendiente de revisión'),     #
            ('APROBADO', 'aprobado'),
            ('RECHAZADO', 'rechazado')
        ],
        default='PENDIENTE',
        help_text="Estado del reporte dentro del sistema",
    )

    def clean(self):
        """
        Validaciones personalizadas del modelo antes de guardar:
        - Verifica si el organismo puede subir ese tipo de medida.
        - Verifica si el usuario está autorizado para subir reportes.
        """
        if not self.tipo_medida.organismos_permitidos.filter(id=self.usuario.organismo_sectorial.id).exists():
            raise ValidationError({
                'tipo_medida': "Esta medida no está permitido para su organismo sectorial."
            }
        )
        if not self.usuario.autorizado_para_reportes:
            raise ValidationError({
                'usuario': "Este usuario no está autorizado para generar reportes."
            }
        )

    def save(self, *args, **kwargs):
        """
            Guardado personalizado que ejecuta las validaciones antes de guardar.
        """
        self.clean()
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
    Modelo que representa una medida que puede ser reportada por organismos sectoriales.

    Cada medida puede ser de cumplimiento obligatorio y estar asociada a uno o más organismos autorizados.
    Ejemplo: "Control emisiones complejo termoeléctrico Ventanas" solo lo reporta la Superintendencia de Electricidad y Combustibles.

    Atributos:
        nombre (str): Nombre identificador de la medida.
        descripcion (str): Detalles adicionales sobre la medida.
        extension_permitida (str): Extensión de archivo permitida (ej: .pdf, .xlsx).
        obligatorio (bool): Define si la medida es de cumplimiento obligatorio.
        organismos_permitidos (ManyToMany): Organismos que pueden reportar esta medida.
    """

    nombre = models.CharField(max_length=100)    
    descripcion = models.TextField(blank=True)
    extension_permitida = models.CharField(max_length=10)

    obligatorio = models.BooleanField(
        default=False,
        help_text="Indica si esta medida es de entrega obligatoria",
    )

    organismos_permitidos = models.ManyToManyField(
        OrganismoSectorial,
        related_name='medidas_permitidas',
        help_text="Organismos autorizados para reportar esta medida"
    )    

    class Meta:
        """
            UniqueConstraint impone restricciones de unicidad en uno o mas campos 
            de la base de datos evitando que se repitan. En este caso, no pueden haber 
            2 tipos de medidas con el mismo nombre. Campo "nombre" debe ser unico en la tabla
        """
        constraints = [
            UniqueConstraint(fields=['nombre'], name='unique_tipo_medida')   
        ]     
        


    def save(self, *args, **kwargs):
        print(f"Guardando Medida: {self.nombre}")  
        super().save(*args, **kwargs)
        print(f"Guardado exitosamente: {self.nombre}")


    def __str__(self):
        organismos = ", ".join([org.codigo_ente for org in self.organismos_permitidos.all()])
        return f"{self.nombre} - Permitido para: {organismos}"
    
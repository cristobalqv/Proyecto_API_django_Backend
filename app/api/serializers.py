from rest_framework import serializers
from app.models import Documento, TipoDocumentoPermitido, OrganismoSectorial

#Aquí validaremos la información entrante para garantizar seguridad e integridad

class TipoDocumentoPermitidoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoDocumentoPermitido
        fields = '__all__'


class DocumentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Documento
        # fields = ['tipo_documento', 'archivo', 'fecha_subida', 'estado']
        # read_only_fields = ['estado']      #campo solo lectura
        fields = '__all__'

    """verificamos que el tipo de documento corresponda al ente fiscalizador
    antes de llegar a este metodo, se crea un diccionario "data" que representa 
    un objeto creado previamente con los campos del modelo "TipoDocumentoPermitido"""
    
    def validate(self, data):     #data corresponde a un diccionario que contiene todos los datos que llegan en la peticion despues de una validacion inicial previo a esta funcion validate()
        usuario = data['usuario']     #asigno la instancia actual del usuario. este tendrá sus atributos definidos
        tipo_doc = data['tipo_documento']     #data['tipo_documento'] va a contener todos los atributos y metodos, ya que mediante ForeignKey el campo tipo_documento de la clase Documento contiene TODOS los atributos de la clase TipoDocumentoPermitido. Se lee de la siguiente forma: <TipoDocumentoPermitido: id=1, tipo_ente= ... >

        # Verificar que el usuario tenga permitido subir este tipo de documento
        if not tipo_doc.entes_permitidos.filter(id=usuario.id).exists():
            raise serializers.ValidationError(
                {"tipo_documento": "Este tipo de documento no está permitido para su usuario."}
            )
        return data



    def create(self, validated_data):     
        """crea el objeto en la base de datos con los datos ya validados
        asigna automaticamente el usuario actual"""
        validated_data['usuario'] = self.context['request'].user
        return super().create(validated_data)



    
class OrganismoSectorialSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganismoSectorial
        fields = '__all__'
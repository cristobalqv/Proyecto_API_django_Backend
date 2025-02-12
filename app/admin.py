from django.contrib import admin

# Register your models here.

from django.contrib.auth.admin import UserAdmin
from app.models import Usuario, Documento, TipoDocumentoPermitido, OrganismoSectorial


class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('username', 'organismo_sectorial', 'autorizado_para_reportes')


class DocumentoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'tipo_documento', 'archivo', 'fecha_subida', 'estado')


class TipoDocumentoPermitidoAdmin(admin.ModelAdmin):     #OJO AQUI
    list_display = ('nombre', 'extension_permitida')
    #'get_organismos_permitidos', 

    def get_organismos_permitidos(self, obj):
        return ", ".join([org.codigo_ente for org in obj.organismos_permitidos.all()])
    
    get_organismos_permitidos.short_description = "Organismos Permitidos"


admin.site.register(Usuario, UsuarioAdmin)
admin.site.register(Documento, DocumentoAdmin)
admin.site.register(TipoDocumentoPermitido, TipoDocumentoPermitidoAdmin)
admin.site.register(OrganismoSectorial)
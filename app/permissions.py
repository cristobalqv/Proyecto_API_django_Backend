from rest_framework.permissions import BasePermission   #para permisos personalizados

class PuedeRevisarReportes(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.has_perm('app.can_review_reports')
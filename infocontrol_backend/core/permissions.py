from rest_framework.permissions import BasePermission

class IsAdminPerfil(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.is_superuser:
            return True

        return hasattr(request.user, 'perfil_usuario') and request.user.perfil_usuario.perfil == 'ADMIN'

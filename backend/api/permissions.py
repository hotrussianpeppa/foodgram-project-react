from rest_framework import permissions


class IsAdminAuthorOrReadOnly(permissions.BasePermission):
    """
    Проверка разрешения для выполнения операций.

    Доступ только для администраторов, авторов.
    """

    def has_permission(self, request, view):
        """Проверяет разрешение для выполнения операции."""
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        """Проверяет разрешение для выполнения операции для объекта."""
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_superuser
                or request.user.is_staff
                or obj.author == request.user)

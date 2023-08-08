from rest_framework import permissions


class IsAuthorOrAdminOrReadOnly(permissions.BasePermission):
    """Доступно для редактирования, если автор или
    администратор, для остальных только чтение."""

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or (request.user.is_authenticated
                    and (request.method == "POST"
                         or obj.author == request.user)))

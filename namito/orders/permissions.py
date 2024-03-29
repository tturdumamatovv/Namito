from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Пользовательский класс разрешений, который разрешает только владельцу объекта
    выполнять действия по изменению или удалению объекта.
    """

    def has_object_permission(self, request, view, obj):
        # Разрешено GET, HEAD, или OPTIONS запросы, которые всегда безопасны.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Проверяем, является ли пользователь владельцем объекта
        return obj.cart.user == request.user

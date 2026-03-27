from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsModerator(BasePermission):
    """Проверяет, является ли пользователь модератором."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.groups.filter(name="Moderators").exists()

    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.groups.filter(name="Moderators").exists()


class IsOwner(BasePermission):
    """Проверяет, является ли пользователь владельцем."""

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if hasattr(obj, "owner"):
            return obj.owner == request.user
        return False


class IsSelfOrReadOnly(BasePermission):
    """
    Права доступа:
    - GET, HEAD, OPTIONS: все авторизованные пользователи
    - PUT, PATCH: только владелец
    - DELETE: владелец или администратор
    """

    def has_object_permission(self, request, view, obj):
        # Проверяем, что пользователь авторизован
        if not request.user or not request.user.is_authenticated:
            return False

        # Безопасные методы (GET, HEAD, OPTIONS) — всем авторизованным
        if request.method in SAFE_METHODS:
            return True

        # DELETE — владелец или администратор
        if request.method == "DELETE":
            # Администратор или суперпользователь может удалять любого
            if request.user.is_staff or request.user.is_superuser:
                return True
            # Обычный пользователь — только свой профиль
            return obj == request.user

        # PUT, PATCH — только владелец
        return obj == request.user

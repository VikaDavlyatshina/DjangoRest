from rest_framework.permissions import BasePermission


class IsModerator(BasePermission):
    """Проверяет, является ли пользователь модератором."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.groups.filter(name='Moderators').exists()

    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.groups.filter(name='Moderators').exists()


class IsOwner(BasePermission):
    """Проверяет, является ли пользователь владельцем."""

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        return False


class IsSelfOrReadOnly(BasePermission):
    """
    Смотреть можно всех,
    редактировать — только себя
    """

    def has_object_permission(self, request, view, obj):

        # GET, HEAD, OPTIONS — можно всем
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True

        # PUT/PATCH — только свой профиль
        return obj == request.user
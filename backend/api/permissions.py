from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAuthorOrReadOnlyPermission(BasePermission):
    """
    Класс с разным уровнем доступа. Если пользователь не авторизован,
    то доступ только к просмотру страницы.
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.author == request.user

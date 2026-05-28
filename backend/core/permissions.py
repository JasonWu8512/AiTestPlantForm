from rest_framework.permissions import BasePermission


def user_in_group(user, group_name):
    return bool(user and user.is_authenticated and user.groups.filter(name=group_name).exists())


class IsAdminRole(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_superuser)


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return bool(request.user and request.user.is_authenticated)
        if not request.user or not request.user.is_authenticated:
            return False
        return bool(
            request.user.is_superuser
            or request.user.groups.filter(name__in=("admin", "tester")).exists()
        )

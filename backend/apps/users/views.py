from django.contrib.auth.models import Group, User
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.serializers import ROLE_NAMES, UserCreateUpdateSerializer, UserSerializer
from core.permissions import IsAdminOrReadOnly
from core.responses import success_response


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        groups = user.groups.values_list("name", flat=True)
        role = "viewer"
        if user.is_superuser or "admin" in groups:
            role = "admin"
        elif "tester" in groups:
            role = "tester"
        return success_response(
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "is_staff": user.is_staff,
                "is_superuser": user.is_superuser,
                "role": role,
            }
        )


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")
        if refresh_token:
            RefreshToken(refresh_token).blacklist()
        return success_response(message="logout success")


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.order_by("-date_joined")
    permission_classes = [IsAdminOrReadOnly]

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return UserCreateUpdateSerializer
        return UserSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        keyword = self.request.query_params.get("keyword")
        if keyword:
            queryset = queryset.filter(username__icontains=keyword)
        return queryset

    def perform_create(self, serializer):
        self._ensure_default_groups()
        serializer.save()

    def perform_update(self, serializer):
        self._ensure_default_groups()
        serializer.save()

    def _ensure_default_groups(self):
        for role_name in ROLE_NAMES:
            Group.objects.get_or_create(name=role_name)

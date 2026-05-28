from rest_framework import filters, viewsets

from apps.projects.models import Project
from apps.projects.serializers import ProjectSerializer
from core.permissions import IsAdminOrReadOnly


class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ["name", "description"]

    def get_queryset(self):
        queryset = Project.objects.select_related("created_by").all()
        status = self.request.query_params.get("status")
        if status:
            queryset = queryset.filter(status=status)
        return queryset

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

import json
import os
from django.conf import settings
from rest_framework import filters, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

from apps.testcases.models import TestCase
from apps.testcases.serializers import TestCaseSerializer
from apps.testcases.services import TestCaseImportExportService
from core.permissions import IsAdminOrReadOnly


class TestCaseViewSet(viewsets.ModelViewSet):
    serializer_class = TestCaseSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ["title", "description", "expected_result"]

    def get_queryset(self):
        queryset = TestCase.objects.select_related("project", "created_by").all()
        project_id = self.request.query_params.get("project")
        priority = self.request.query_params.get("priority")
        status_filter = self.request.query_params.get("status")
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        if priority:
            queryset = queryset.filter(priority=priority)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        return queryset

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=False, methods=["get"])
    def export_excel(self, request):
        """导出测试用例为 Excel"""
        project_id = request.query_params.get("project")
        if not project_id:
            return Response({"error": "请指定项目ID"}, status=status.HTTP_400_BAD_REQUEST)
        
        testcases = TestCase.objects.filter(project_id=project_id)
        if not testcases.exists():
            return Response({"error": "该项目中没有测试用例"}, status=status.HTTP_404_NOT_FOUND)
        
        # 生成文件路径
        file_name = f"testcases_project_{project_id}.xlsx"
        file_path = os.path.join(settings.MEDIA_ROOT, "exports", file_name)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        result = TestCaseImportExportService.export_to_excel(list(testcases), file_path)
        download_url = f"/media/exports/{file_name}"
        
        return Response({
            "success": True,
            "count": result["count"],
            "download_url": download_url,
        })

    @action(detail=False, methods=["get"])
    def export_json(self, request):
        """导出测试用例为 JSON"""
        project_id = request.query_params.get("project")
        if not project_id:
            return Response({"error": "请指定项目ID"}, status=status.HTTP_400_BAD_REQUEST)
        
        testcases = TestCase.objects.filter(project_id=project_id)
        if not testcases.exists():
            return Response({"error": "该项目中没有测试用例"}, status=status.HTTP_404_NOT_FOUND)
        
        result = TestCaseImportExportService.export_to_json(list(testcases))
        return Response({
            "success": True,
            "count": result["count"],
            "data": result["data"],
        })

    @action(detail=False, methods=["post"])
    def import_excel(self, request):
        """从 Excel 导入测试用例"""
        project_id = request.data.get("project")
        if not project_id:
            return Response({"error": "请指定项目ID"}, status=status.HTTP_400_BAD_REQUEST)
        
        uploaded_file = request.FILES.get("file")
        if not uploaded_file:
            return Response({"error": "请上传文件"}, status=status.HTTP_400_BAD_REQUEST)
        
        # 保存上传的文件
        file_name = f"import_{uploaded_file.name}"
        file_path = os.path.join(settings.MEDIA_ROOT, "imports", file_name)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, "wb") as f:
            for chunk in uploaded_file.chunks():
                f.write(chunk)
        
        result = TestCaseImportExportService.import_from_excel(file_path, project_id, request.user)
        
        # 清理上传的文件
        try:
            os.remove(file_path)
        except:
            pass
        
        if result["success"]:
            return Response({
                "success": True,
                "imported_count": result["imported_count"],
                "error_rows": result.get("error_rows", []),
            })
        else:
            return Response({"error": result["error"]}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"])
    def import_json(self, request):
        """从 JSON 导入测试用例"""
        project_id = request.data.get("project")
        if not project_id:
            return Response({"error": "请指定项目ID"}, status=status.HTTP_400_BAD_REQUEST)
        
        json_data = request.data.get("data")
        if not json_data:
            return Response({"error": "请提供 JSON 数据"}, status=status.HTTP_400_BAD_REQUEST)
        
        if isinstance(json_data, str):
            try:
                json_data = json.loads(json_data)
            except json.JSONDecodeError:
                return Response({"error": "JSON 格式错误"}, status=status.HTTP_400_BAD_REQUEST)
        
        result = TestCaseImportExportService.import_from_json(json_data, project_id, request.user)
        
        if result["success"]:
            return Response({
                "success": True,
                "imported_count": result["imported_count"],
                "error_items": result.get("error_items", []),
            })
        else:
            return Response({"error": result["error"]}, status=status.HTTP_400_BAD_REQUEST)

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import NotificationConfig, NotificationRecord
from .serializers import NotificationConfigSerializer, NotificationRecordSerializer
from .services.dingtalk import DingTalkNotifier
from django.db.models import Q


class NotificationConfigViewSet(viewsets.ModelViewSet):
    queryset = NotificationConfig.objects.all()
    serializer_class = NotificationConfigSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def test_send(self, request, pk=None):
        config = self.get_object()
        if config.type == 'dingtalk':
            notifier = DingTalkNotifier()
            result = notifier.send_text_message('测试消息：这是一条测试通知，用于验证钉钉通知配置是否正确。')
            return Response(result)
        return Response({'success': False, 'message': '不支持的通知类型'})


class NotificationRecordViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = NotificationRecord.objects.all()
    serializer_class = NotificationRecordSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        type_param = self.request.query_params.get('type')
        status_param = self.request.query_params.get('status')
        
        if type_param:
            queryset = queryset.filter(type=type_param)
        if status_param:
            queryset = queryset.filter(status=status_param)
        
        return queryset

    @action(detail=True, methods=['post'])
    def resend(self, request, pk=None):
        record = self.get_object()
        if record.config and record.config.type == 'dingtalk':
            notifier = DingTalkNotifier()
            result = notifier.send_markdown_message(record.title, record.content)
            if result['success']:
                record.status = 'sent'
                record.error_message = None
                record.save()
            else:
                record.error_message = result['message']
                record.save()
            return Response(result)
        return Response({'success': False, 'message': '无法重发此通知'})
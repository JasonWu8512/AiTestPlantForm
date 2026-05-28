from rest_framework import serializers
from .models import NotificationConfig, NotificationRecord


class NotificationConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationConfig
        fields = '__all__'
        read_only_fields = ['created_by', 'created_at', 'updated_at']


class NotificationRecordSerializer(serializers.ModelSerializer):
    config_name = serializers.CharField(source='config.name', read_only=True)
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = NotificationRecord
        fields = '__all__'
        read_only_fields = ['created_at', 'sent_at']
from django.db import models
from django.contrib.auth.models import User


class NotificationConfig(models.Model):
    NOTIFICATION_TYPE_CHOICES = [
        ('dingtalk', '钉钉'),
        ('email', '邮件'),
    ]

    name = models.CharField(max_length=100, verbose_name='配置名称')
    type = models.CharField(max_length=20, choices=NOTIFICATION_TYPE_CHOICES, verbose_name='通知类型')
    webhook_url = models.URLField(blank=True, null=True, verbose_name='Webhook地址')
    access_token = models.CharField(max_length=255, blank=True, null=True, verbose_name='访问令牌')
    secret = models.CharField(max_length=255, blank=True, null=True, verbose_name='密钥')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='创建人')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '通知配置'
        verbose_name_plural = '通知配置'

    def __str__(self):
        return self.name


class NotificationRecord(models.Model):
    STATUS_CHOICES = [
        ('pending', '待发送'),
        ('sent', '已发送'),
        ('failed', '发送失败'),
    ]

    TYPE_CHOICES = [
        ('report', '报告通知'),
        ('execution', '执行通知'),
        ('system', '系统通知'),
    ]

    config = models.ForeignKey(NotificationConfig, on_delete=models.SET_NULL, null=True, verbose_name='配置')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name='通知类型')
    title = models.CharField(max_length=200, verbose_name='通知标题')
    content = models.TextField(verbose_name='通知内容')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='状态')
    error_message = models.TextField(blank=True, null=True, verbose_name='错误信息')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    sent_at = models.DateTimeField(blank=True, null=True, verbose_name='发送时间')

    class Meta:
        verbose_name = '通知记录'
        verbose_name_plural = '通知记录'

    def __str__(self):
        return f"{self.get_type_display()} - {self.title}"
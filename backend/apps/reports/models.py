from django.db import models

from apps.executions.models import TestExecution


class TestReport(models.Model):
    STATUS_CHOICES = (
        ("pending", "待生成"),
        ("generated", "已生成"),
        ("failed", "生成失败"),
    )

    execution = models.OneToOneField(TestExecution, verbose_name="执行记录", on_delete=models.CASCADE, related_name="report")
    name = models.CharField("报告名称", max_length=150)
    summary = models.JSONField("报告摘要", default=dict, blank=True)
    allure_report_path = models.CharField("Allure 报告入口", max_length=500, blank=True)
    status = models.CharField("生成状态", max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "测试报告"
        verbose_name_plural = "测试报告"

    def __str__(self):
        return self.name

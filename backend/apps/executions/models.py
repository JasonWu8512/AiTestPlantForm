from django.conf import settings
from django.db import models

from apps.testcases.models import TestCase
from apps.testplans.models import TestPlan


class TestExecution(models.Model):
    STATUS_CHOICES = (
        ("pending", "待执行"),
        ("running", "执行中"),
        ("completed", "已完成"),
        ("failed", "执行失败"),
        ("canceled", "已取消"),
    )

    plan = models.ForeignKey(TestPlan, verbose_name="测试计划", on_delete=models.CASCADE, related_name="executions")
    executor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="执行人",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="test_executions",
    )
    status = models.CharField("执行状态", max_length=20, choices=STATUS_CHOICES, default="pending")
    started_at = models.DateTimeField("实际开始时间", null=True, blank=True)
    finished_at = models.DateTimeField("实际结束时间", null=True, blank=True)
    celery_task_id = models.CharField("异步任务 ID", max_length=100, blank=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "测试执行"
        verbose_name_plural = "测试执行"


class TestResult(models.Model):
    STATUS_CHOICES = (
        ("passed", "通过"),
        ("failed", "失败"),
        ("blocked", "阻塞"),
        ("skipped", "跳过"),
    )

    execution = models.ForeignKey(TestExecution, verbose_name="执行记录", on_delete=models.CASCADE, related_name="results")
    testcase = models.ForeignKey(TestCase, verbose_name="测试用例", on_delete=models.CASCADE, related_name="results")
    status = models.CharField("结果状态", max_length=20, choices=STATUS_CHOICES)
    actual_result = models.TextField("实际结果", blank=True)
    remark = models.TextField("备注", blank=True)
    attachments = models.JSONField("附件信息", default=list, blank=True)
    executed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="执行人",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="test_results",
    )
    executed_at = models.DateTimeField("执行时间", null=True, blank=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        ordering = ("testcase_id",)
        constraints = [
            models.UniqueConstraint(fields=["execution", "testcase"], name="unique_testcase_result_in_execution"),
        ]
        verbose_name = "测试结果"
        verbose_name_plural = "测试结果"

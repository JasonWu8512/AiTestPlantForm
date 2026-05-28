from django.conf import settings
from django.db import models

from apps.projects.models import Project


class TestCase(models.Model):
    PRIORITY_CHOICES = (
        ("P0", "P0"),
        ("P1", "P1"),
        ("P2", "P2"),
        ("P3", "P3"),
    )
    STATUS_CHOICES = (
        ("draft", "草稿"),
        ("active", "启用"),
        ("archived", "归档"),
    )

    project = models.ForeignKey(Project, verbose_name="所属项目", on_delete=models.CASCADE, related_name="testcases")
    title = models.CharField("用例标题", max_length=200)
    description = models.TextField("用例描述", blank=True)
    precondition = models.TextField("前置条件", blank=True)
    steps = models.JSONField("测试步骤", default=list, blank=True)
    expected_result = models.TextField("预期结果", blank=True)
    priority = models.CharField("优先级", max_length=2, choices=PRIORITY_CHOICES, default="P2")
    status = models.CharField("状态", max_length=20, choices=STATUS_CHOICES, default="draft")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="创建人",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="created_testcases",
    )
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "测试用例"
        verbose_name_plural = "测试用例"

    def __str__(self):
        return self.title

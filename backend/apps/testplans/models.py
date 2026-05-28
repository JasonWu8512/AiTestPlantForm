from django.conf import settings
from django.db import models

from apps.projects.models import Project
from apps.testcases.models import TestCase


class TestPlan(models.Model):
    STATUS_CHOICES = (
        ("draft", "草稿"),
        ("active", "启用"),
        ("archived", "归档"),
    )

    project = models.ForeignKey(Project, verbose_name="所属项目", on_delete=models.CASCADE, related_name="testplans")
    name = models.CharField("计划名称", max_length=150)
    description = models.TextField("计划描述", blank=True)
    status = models.CharField("状态", max_length=20, choices=STATUS_CHOICES, default="draft")
    start_time = models.DateTimeField("计划开始时间", null=True, blank=True)
    end_time = models.DateTimeField("计划结束时间", null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="创建人",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="created_testplans",
    )
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "测试计划"
        verbose_name_plural = "测试计划"

    def __str__(self):
        return self.name


class TestPlanCase(models.Model):
    plan = models.ForeignKey(TestPlan, verbose_name="测试计划", on_delete=models.CASCADE, related_name="plan_cases")
    testcase = models.ForeignKey(TestCase, verbose_name="测试用例", on_delete=models.CASCADE, related_name="plan_cases")
    sort_order = models.PositiveIntegerField("执行顺序", default=0)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)

    class Meta:
        ordering = ("sort_order", "id")
        constraints = [
            models.UniqueConstraint(fields=["plan", "testcase"], name="unique_testcase_in_plan"),
        ]
        verbose_name = "测试计划用例"
        verbose_name_plural = "测试计划用例"

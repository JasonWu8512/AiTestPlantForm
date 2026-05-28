from django.conf import settings
from django.db import models

from apps.projects.models import Project


class ApiTestCase(models.Model):
    METHOD_CHOICES = (
        ("GET", "GET"),
        ("POST", "POST"),
        ("PUT", "PUT"),
        ("DELETE", "DELETE"),
        ("PATCH", "PATCH"),
    )
    BODY_TYPE_CHOICES = (
        ("none", "无"),
        ("json", "JSON"),
        ("form-data", "表单数据"),
        ("x-www-form-urlencoded", "URL编码表单"),
        ("raw", "原始文本"),
    )
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

    project = models.ForeignKey(Project, verbose_name="所属项目", on_delete=models.CASCADE, related_name="api_testcases")
    name = models.CharField("用例名称", max_length=200)
    description = models.TextField("用例描述", blank=True)
    method = models.CharField("请求方法", max_length=10, choices=METHOD_CHOICES, default="GET")
    url = models.CharField("请求 URL", max_length=500)
    headers = models.JSONField("请求头", default=dict, blank=True)
    params = models.JSONField("URL 参数", default=dict, blank=True)
    body_type = models.CharField("请求体类型", max_length=30, choices=BODY_TYPE_CHOICES, default="none")
    body = models.JSONField("请求体", default=dict, blank=True)
    expected_status = models.IntegerField("期望状态码", default=200)
    validation_rules = models.JSONField("验证规则", default=list, blank=True)
    timeout = models.IntegerField("超时时间(秒)", default=30)
    priority = models.CharField("优先级", max_length=2, choices=PRIORITY_CHOICES, default="P2")
    status = models.CharField("状态", max_length=20, choices=STATUS_CHOICES, default="draft")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="创建人",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="created_api_testcases",
    )
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "接口测试用例"
        verbose_name_plural = "接口测试用例"

    def __str__(self):
        return f"{self.method} {self.name}"


class ApiTestExecution(models.Model):
    STATUS_CHOICES = (
        ("pending", "待执行"),
        ("running", "执行中"),
        ("completed", "已完成"),
        ("failed", "执行失败"),
        ("canceled", "已取消"),
    )

    project = models.ForeignKey(Project, verbose_name="所属项目", on_delete=models.CASCADE, related_name="api_executions", null=True, blank=True)
    name = models.CharField("执行名称", max_length=200)
    status = models.CharField("执行状态", max_length=20, choices=STATUS_CHOICES, default="pending")
    total = models.IntegerField("总数", default=0)
    passed = models.IntegerField("通过数", default=0)
    failed = models.IntegerField("失败数", default=0)
    executor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="执行人",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="api_test_executions",
    )
    started_at = models.DateTimeField("开始时间", null=True, blank=True)
    finished_at = models.DateTimeField("结束时间", null=True, blank=True)
    celery_task_id = models.CharField("异步任务 ID", max_length=100, blank=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "接口测试执行"
        verbose_name_plural = "接口测试执行"

    def __str__(self):
        return self.name

    @property
    def pass_rate(self):
        if self.total == 0:
            return 0
        return round(self.passed / self.total * 100, 2)


class ApiTestResult(models.Model):
    STATUS_CHOICES = (
        ("passed", "通过"),
        ("failed", "失败"),
        ("error", "错误"),
    )

    execution = models.ForeignKey(ApiTestExecution, verbose_name="执行记录", on_delete=models.CASCADE, related_name="results")
    testcase = models.ForeignKey(ApiTestCase, verbose_name="测试用例", on_delete=models.CASCADE, related_name="results")
    status = models.CharField("结果状态", max_length=20, choices=STATUS_CHOICES)
    response_status = models.IntegerField("响应状态码", null=True, blank=True)
    response_body = models.JSONField("响应体", default=dict, blank=True)
    response_time = models.IntegerField("响应时间(ms)", null=True, blank=True)
    validation_results = models.JSONField("验证结果", default=list, blank=True)
    error_message = models.TextField("错误信息", blank=True)
    executed_at = models.DateTimeField("执行时间", null=True, blank=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)

    class Meta:
        ordering = ("testcase_id",)
        verbose_name = "接口测试结果"
        verbose_name_plural = "接口测试结果"

    def __str__(self):
        return f"{self.testcase.name} - {self.status}"

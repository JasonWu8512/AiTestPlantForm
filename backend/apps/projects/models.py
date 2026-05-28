from django.conf import settings
from django.db import models


class Project(models.Model):
    STATUS_ACTIVE = "active"
    STATUS_ARCHIVED = "archived"
    STATUS_CHOICES = (
        (STATUS_ACTIVE, "启用"),
        (STATUS_ARCHIVED, "归档"),
    )

    name = models.CharField("项目名称", max_length=100, unique=True)
    description = models.TextField("项目描述", blank=True)
    status = models.CharField("状态", max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="创建人",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="created_projects",
    )
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "项目"
        verbose_name_plural = "项目"

    def __str__(self):
        return self.name

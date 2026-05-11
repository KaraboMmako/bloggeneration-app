from django.db import models
from apps.blogs.models import BlogProject


class ContentBrief(models.Model):
    project = models.OneToOneField(
        BlogProject,
        on_delete=models.CASCADE,
        related_name="brief",
    )
    prompt = models.TextField()
    title_guidance = models.CharField(max_length=255, blank=True)
    tone = models.CharField(max_length=100, blank=True)
    audience = models.CharField(max_length=255, blank=True)
    objective = models.TextField(blank=True)
    keywords = models.JSONField(default=list, blank=True)
    writing_style = models.CharField(max_length=100, blank=True)
    instructions = models.TextField(blank=True)
    desired_length = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Brief for {self.project.name}"
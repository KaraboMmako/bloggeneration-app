# revisions/models.py
from django.db import models
from apps.blogs.models import BlogProject

class BlogRevision(models.Model):
    project = models.ForeignKey(BlogProject, on_delete=models.CASCADE, related_name="revisions")
    version_number = models.PositiveIntegerField()
    title = models.CharField(max_length=255, blank=True)
    full_content = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
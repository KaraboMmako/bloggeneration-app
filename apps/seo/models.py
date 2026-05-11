# seo/models.py
from django.db import models
from apps.blogs.models import BlogProject

class SEOData(models.Model):
    project = models.OneToOneField(BlogProject, on_delete=models.CASCADE, related_name="seo")
    meta_title = models.CharField(max_length=255, blank=True)
    meta_description = models.TextField(blank=True)
    focus_keyword = models.CharField(max_length=255, blank=True)
    secondary_keywords = models.JSONField(default=list, blank=True)
    canonical_url = models.URLField(blank=True)
    schema_markup = models.JSONField(default=dict, blank=True)
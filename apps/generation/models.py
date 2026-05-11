# generation/models.py
from django.db import models
from apps.blogs.models import BlogProject

class BlogOutline(models.Model):
    project = models.OneToOneField(BlogProject, on_delete=models.CASCADE, related_name="outline")
    raw_outline = models.JSONField(default=list, blank=True)
    intro_instruction = models.TextField(blank=True)
    conclusion_instruction = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class BlogSection(models.Model):
    SECTION_TYPES = [
        ("intro", "Intro"),
        ("body", "Body"),
        ("conclusion", "Conclusion"),
        ("cta", "CTA"),
    ]

    project = models.ForeignKey(
        BlogProject,
        on_delete=models.CASCADE,
        related_name="sections"
    )
    section_type = models.CharField(max_length=20, choices=SECTION_TYPES, default="body")
    heading = models.CharField(max_length=255, blank=True)
    order = models.PositiveIntegerField(default=0)
    content = models.TextField(blank=True)
    generation_prompt = models.TextField(blank=True)
    is_generated = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.project.name} - {self.heading or self.section_type}"
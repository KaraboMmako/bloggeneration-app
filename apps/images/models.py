from django.db import models
from apps.blogs.models import BlogProject
from apps.generation.models import BlogSection


class BlogImage(models.Model):
    IMAGE_TYPES = [
        ("hero", "Hero"),
        ("section", "Section"),
    ]

    project = models.ForeignKey(
        BlogProject,
        on_delete=models.CASCADE,
        related_name="images",
    )
    
    section = models.ForeignKey(
        BlogSection,
        on_delete=models.CASCADE,
        related_name="images",
        null=True,
        blank=True,
    )
    image_type = models.CharField(max_length=20, choices=IMAGE_TYPES)
    prompt = models.TextField()
    image_url = models.URLField(blank=True)
    alt_text = models.CharField(max_length=255, blank=True)
    order = models.PositiveIntegerField(default=0)
    is_generated = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "created_at"]

    def __str__(self):
        return f"{self.project.name} - {self.image_type}"
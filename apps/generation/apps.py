from django.apps import AppConfig
from pathlib import Path


class GenerationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.generation"
    path = str(Path(__file__).resolve().parent)

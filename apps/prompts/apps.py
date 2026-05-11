from django.apps import AppConfig
from pathlib import Path


class PromptsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.prompts"
    path = str(Path(__file__).resolve().parent)

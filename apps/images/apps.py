from django.apps import AppConfig
from pathlib import Path


class ImagesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.images"
    path = str(Path(__file__).resolve().parent)

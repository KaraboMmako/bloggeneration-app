from django.apps import AppConfig
from pathlib import Path


class SeoConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.seo"
    path = str(Path(__file__).resolve().parent)

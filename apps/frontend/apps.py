from django.apps import AppConfig
from pathlib import Path


class FrontendConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.frontend"
    path = str(Path(__file__).resolve().parent)

from django.apps import AppConfig
from pathlib import Path


class RevisionsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.revisions"
    path = str(Path(__file__).resolve().parent)

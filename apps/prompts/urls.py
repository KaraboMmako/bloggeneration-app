from django.urls import path
from .views import ContentBriefView

urlpatterns = [
    path("projects/<int:pk>/brief/", ContentBriefView.as_view(), name="project-brief"),
]
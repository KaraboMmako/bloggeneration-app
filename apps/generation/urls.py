from django.urls import path
from .views import (
    GenerateOutlineView,
    BlogOutlineDetailView,
    GenerateSectionsView,
    ProjectSectionsView,
    FullBlogView,
    RegenerateSectionView,
    RegenerateBlogView,
)

urlpatterns = [
    path("projects/<int:pk>/generate-outline/", GenerateOutlineView.as_view(), name="generate-outline"),
    path("projects/<int:pk>/outline/", BlogOutlineDetailView.as_view(), name="project-outline"),
    path("projects/<int:pk>/generate-sections/", GenerateSectionsView.as_view(), name="generate-sections"),
    path("projects/<int:pk>/sections/", ProjectSectionsView.as_view(), name="project-sections"),
    path("projects/<int:pk>/full-blog/", FullBlogView.as_view(), name="full-blog"),
    path("projects/<int:pk>/regenerate/", RegenerateBlogView.as_view(), name="regenerate-blog"),
    path("sections/<int:section_id>/regenerate/", RegenerateSectionView.as_view(), name="regenerate-section"),
]
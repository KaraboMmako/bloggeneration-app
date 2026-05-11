from django.urls import path
from .views import (
    GenerateHeroImageView,
    HeroImageDetailView,
    GenerateSectionImageView,
    SectionImagesListView,
)

urlpatterns = [
    path("projects/<int:pk>/generate-image/", GenerateHeroImageView.as_view(), name="generate-project-image"),
    path("projects/<int:pk>/generate-hero-image/", GenerateHeroImageView.as_view(), name="generate-hero-image"),
    path("projects/<int:pk>/hero-image/", HeroImageDetailView.as_view(), name="hero-image-detail"),
    path("sections/<int:section_id>/generate-image/", GenerateSectionImageView.as_view(), name="generate-section-image"),
    path("sections/<int:section_id>/images/", SectionImagesListView.as_view(), name="section-images-list"),
]
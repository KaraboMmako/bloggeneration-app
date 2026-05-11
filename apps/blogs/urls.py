from rest_framework.routers import DefaultRouter
from .views import BlogProjectViewSet

router = DefaultRouter()
router.register("", BlogProjectViewSet, basename="projects")

urlpatterns = router.urls
from rest_framework import viewsets, permissions
from .models import BlogProject
from .serializers import BlogProjectSerializer


class BlogProjectViewSet(viewsets.ModelViewSet):
    serializer_class = BlogProjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return BlogProject.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.blogs.models import BlogProject
from .models import ContentBrief
from .serializers import ContentBriefSerializer


class ContentBriefView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_project(self, pk, user):
        return BlogProject.objects.get(pk=pk, user=user)

    def get(self, request, pk):
        project = self.get_project(pk, request.user)
        brief = getattr(project, "brief", None)

        if not brief:
            return Response({"detail": "Brief not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ContentBriefSerializer(brief)
        return Response(serializer.data)

    def post(self, request, pk):
        project = self.get_project(pk, request.user)

        if hasattr(project, "brief"):
            return Response(
                {"detail": "Brief already exists for this project."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = ContentBriefSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(project=project)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def patch(self, request, pk):
        project = self.get_project(pk, request.user)
        brief = getattr(project, "brief", None)

        if not brief:
            return Response({"detail": "Brief not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ContentBriefSerializer(brief, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.blogs.models import BlogProject
from apps.generation.models import BlogSection
from .models import BlogImage
from .serializers import BlogImageSerializer
from .services import (
    generate_hero_image_prompt,
    generate_section_image_prompt,
    generate_image_from_prompt,
)


class GenerateHeroImageView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            project = BlogProject.objects.get(pk=pk, user=request.user)
        except BlogProject.DoesNotExist:
            return Response(
                {"detail": "Project not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            prompt = generate_hero_image_prompt(project)
            image_url = generate_image_from_prompt(prompt)
        except Exception as exc:
            return Response(
                {"detail": f"Image generation failed: {exc}"},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        image, _ = BlogImage.objects.update_or_create(
            project=project,
            section=None,
            image_type="hero",
            defaults={
                "prompt": prompt,
                "image_url": image_url,
                "alt_text": f"Hero image for {project.name}",
                "order": 0,
                "is_generated": True,
            },
        )

        serializer = BlogImageSerializer(image, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class HeroImageDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        try:
            project = BlogProject.objects.get(pk=pk, user=request.user)
        except BlogProject.DoesNotExist:
            return Response(
                {"detail": "Project not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            image = BlogImage.objects.get(
                project=project,
                section=None,
                image_type="hero",
            )
        except BlogImage.DoesNotExist:
            return Response(
                {"detail": "Hero image not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = BlogImageSerializer(image, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class GenerateSectionImageView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, section_id):
        try:
            section = BlogSection.objects.select_related("project").get(
                id=section_id,
                project__user=request.user,
            )
        except BlogSection.DoesNotExist:
            return Response(
                {"detail": "Section not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            prompt = generate_section_image_prompt(section)
            image_url = generate_image_from_prompt(prompt)
        except Exception as exc:
            return Response(
                {"detail": f"Image generation failed: {exc}"},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        image, _ = BlogImage.objects.update_or_create(
            project=section.project,
            section=section,
            image_type="section",
            defaults={
                "prompt": prompt,
                "image_url": image_url,
                "alt_text": f"Image for section {section.heading}",
                "order": section.order,
                "is_generated": True,
            },
        )

        serializer = BlogImageSerializer(image, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class SectionImagesListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, section_id):
        try:
            section = BlogSection.objects.select_related("project").get(
                id=section_id,
                project__user=request.user,
            )
        except BlogSection.DoesNotExist:
            return Response(
                {"detail": "Section not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        images = BlogImage.objects.filter(section=section).order_by("order", "created_at")
        serializer = BlogImageSerializer(images, many=True, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)
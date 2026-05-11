from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.blogs.models import BlogProject
from .models import BlogOutline, BlogSection
from .serializers import BlogOutlineSerializer, BlogSectionSerializer
from .services import generate_outline_from_brief
from .services import generate_section_content
from .services import assemble_full_blog
from .services import render_blog_markdown


class GenerateOutlineView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            project = BlogProject.objects.get(pk=pk, user=request.user)
        except BlogProject.DoesNotExist:
            return Response(
                {"detail": "Project not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        brief = getattr(project, "brief", None)
        if not brief:
            return Response(
                {"detail": "Content brief not found for this project."},
                status=status.HTTP_400_BAD_REQUEST
            )

        outline_data = generate_outline_from_brief(brief)

        outline, created = BlogOutline.objects.update_or_create(
            project=project,
            defaults={
                "raw_outline": outline_data.get("raw_outline", []),
                "intro_instruction": outline_data.get("intro_instruction", ""),
                "conclusion_instruction": outline_data.get("conclusion_instruction", ""),
            }
        )

        serializer = BlogOutlineSerializer(outline)
        return Response(serializer.data, status=status.HTTP_200_OK)


class BlogOutlineDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        try:
            project = BlogProject.objects.get(pk=pk, user=request.user)
        except BlogProject.DoesNotExist:
            return Response(
                {"detail": "Project not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        outline = getattr(project, "outline", None)
        if not outline:
            return Response(
                {"detail": "Outline not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = BlogOutlineSerializer(outline)
        return Response(serializer.data)


class GenerateSectionsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            project = BlogProject.objects.get(pk=pk, user=request.user)
        except BlogProject.DoesNotExist:
            return Response(
                {"detail": "Project not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        brief = getattr(project, "brief", None)
        if not brief:
            return Response(
                {"detail": "Content brief not found for this project."},
                status=status.HTTP_400_BAD_REQUEST
            )

        outline = getattr(project, "outline", None)
        if not outline:
            return Response(
                {"detail": "Outline not found. Generate an outline first."},
                status=status.HTTP_400_BAD_REQUEST
            )

        raw_outline = outline.raw_outline or []
        if not isinstance(raw_outline, list) or not raw_outline:
            return Response(
                {"detail": "Outline has no body sections to generate from."},
                status=status.HTTP_400_BAD_REQUEST
            )

        BlogSection.objects.filter(project=project).delete()

        created_sections = []

        intro_content = generate_section_content(
            title="Introduction",
            instruction=outline.intro_instruction or "",
            tone=brief.tone,
            audience=brief.audience,
            writing_style=brief.writing_style,
        )
        created_sections.append(
            BlogSection.objects.create(
                project=project,
                section_type="intro",
                heading="Introduction",
                order=0,
                content=intro_content,
                generation_prompt=outline.intro_instruction or "",
                is_generated=True,
            )
        )

        for index, item in enumerate(raw_outline, start=1):
            heading = item.get("heading", f"Section {index}") if isinstance(item, dict) else f"Section {index}"
            notes = item.get("notes", "") if isinstance(item, dict) else ""

            body_content = generate_section_content(
                title=heading,
                instruction=notes,
                tone=brief.tone,
                audience=brief.audience,
                writing_style=brief.writing_style,
            )

            created_sections.append(
                BlogSection.objects.create(
                    project=project,
                    section_type="body",
                    heading=heading,
                    order=index,
                    content=body_content,
                    generation_prompt=notes,
                    is_generated=True,
                )
            )

        conclusion_content = generate_section_content(
            title="Conclusion",
            instruction=outline.conclusion_instruction or "",
            tone=brief.tone,
            audience=brief.audience,
            writing_style=brief.writing_style,
        )
        created_sections.append(
            BlogSection.objects.create(
                project=project,
                section_type="conclusion",
                heading="Conclusion",
                order=len(raw_outline) + 1,
                content=conclusion_content,
                generation_prompt=outline.conclusion_instruction or "",
                is_generated=True,
            )
        )

        serializer = BlogSectionSerializer(created_sections, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ProjectSectionsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        try:
            project = BlogProject.objects.get(pk=pk, user=request.user)
        except BlogProject.DoesNotExist:
            return Response(
                {"detail": "Project not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        sections = BlogSection.objects.filter(project=project).order_by("order", "id")
        serializer = BlogSectionSerializer(sections, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class FullBlogView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def _build_full_blog_response(self, request, pk):
        try:
            project = BlogProject.objects.get(pk=pk, user=request.user)
        except BlogProject.DoesNotExist:
            return Response(
                {"detail": "Project not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        if not project.sections.exists():
            return Response(
                {"detail": "No sections found. Generate sections first."},
                status=status.HTTP_400_BAD_REQUEST
            )

        full_blog = assemble_full_blog(project)

        return Response({
            "project": project.id,
            "content": full_blog,
            "content_html": render_blog_markdown(full_blog) or "",
        })

    def get(self, request, pk):
        return self._build_full_blog_response(request, pk)

    def post(self, request, pk):
        return self._build_full_blog_response(request, pk)


class RegenerateSectionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, section_id):
        try:
            section = BlogSection.objects.select_related("project").get(
                id=section_id,
                project__user=request.user
            )
        except BlogSection.DoesNotExist:
            return Response(
                {"detail": "Section not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        brief = getattr(section.project, "brief", None)
        if not brief:
            return Response(
                {"detail": "Content brief not found for this project."},
                status=status.HTTP_400_BAD_REQUEST
            )

        extra_instruction = request.data.get("extra_instruction", "")
        tone = request.data.get("tone", brief.tone)
        audience = request.data.get("audience", brief.audience)
        writing_style = request.data.get("writing_style", brief.writing_style)

        final_instruction = section.generation_prompt
        if extra_instruction:
            final_instruction += f"\n\nAdditional instruction:\n{extra_instruction}"

        new_content = generate_section_content(
            title=section.heading,
            instruction=final_instruction,
            tone=tone,
            audience=audience,
            writing_style=writing_style,
        )

        section.content = new_content
        section.generation_prompt = final_instruction
        section.is_generated = True
        section.save(update_fields=["content", "generation_prompt", "is_generated", "updated_at"])

        serializer = BlogSectionSerializer(section)
        return Response(serializer.data, status=status.HTTP_200_OK)

class RegenerateBlogView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            project = BlogProject.objects.get(pk=pk, user=request.user)
        except BlogProject.DoesNotExist:
            return Response(
                {"detail": "Project not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        brief = getattr(project, "brief", None)
        if not brief:
            return Response(
                {"detail": "Content brief not found for this project."},
                status=status.HTTP_400_BAD_REQUEST
            )

        outline_data = generate_outline_from_brief(brief)

        BlogOutline.objects.update_or_create(
            project=project,
            defaults={
                "raw_outline": outline_data.get("raw_outline", []),
                "intro_instruction": outline_data.get("intro_instruction", ""),
                "conclusion_instruction": outline_data.get("conclusion_instruction", ""),
            }
        )

        project.sections.all().delete()

        return Response(
            {"detail": "Blog regenerated successfully. Now call generate-sections."},
            status=status.HTTP_200_OK
        )
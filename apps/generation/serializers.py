from rest_framework import serializers
from .models import BlogOutline, BlogSection


class BlogOutlineSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogOutline
        fields = [
            "id",
            "project",
            "raw_outline",
            "intro_instruction",
            "conclusion_instruction",
            "created_at",
        ]
        read_only_fields = ["id", "project", "created_at"]


class BlogSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogSection
        fields = [
            "id",
            "project",
            "section_type",
            "heading",
            "order",
            "content",
            "generation_prompt",
            "is_generated",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "project",
            "created_at",
            "updated_at",
        ]
from rest_framework import serializers
from .models import ContentBrief


class ContentBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentBrief
        fields = [
            "id",
            "project",
            "prompt",
            "title_guidance",
            "tone",
            "audience",
            "objective",
            "keywords",
            "writing_style",
            "instructions",
            "desired_length",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "project", "created_at", "updated_at"]
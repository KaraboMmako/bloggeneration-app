from rest_framework import serializers
from .models import BlogProject


class BlogProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogProject
        fields = ["id", "name", "status", "created_at", "updated_at"]
        read_only_fields = ["id", "status", "created_at", "updated_at"]
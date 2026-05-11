from rest_framework import serializers
from .models import BlogImage


class BlogImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = BlogImage
        fields = [
            "id",
            "project",
            "section",
            "image_type",
            "prompt",
            "image_url",
            "alt_text",
            "order",
            "is_generated",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "project",
            "section",
            "created_at",
        ]

    def get_image_url(self, obj):
        image_url = obj.image_url
        if not image_url:
            return image_url

        request = self.context.get("request")
        if request and image_url.startswith("/"):
            return request.build_absolute_uri(image_url)

        return image_url
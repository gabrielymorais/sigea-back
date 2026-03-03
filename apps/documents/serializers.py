from rest_framework import serializers
from rest_framework.reverse import reverse

from .models import Document


class DocumentSerializer(serializers.ModelSerializer):
    owner_id = serializers.IntegerField(source="owner.id", read_only=True)
    file_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Document
        fields = [
            "id",
            "owner_id",
            "name",
            "doc_type",
            "file",
            "file_url",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "owner_id", "file_url", "created_at", "updated_at"]

    def get_file_url(self, obj: Document):
        request = self.context.get("request")
        if not obj.file:
            return None

        return reverse("documents-download", kwargs={"pk": obj.pk}, request=request)
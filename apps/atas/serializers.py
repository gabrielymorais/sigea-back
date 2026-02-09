from rest_framework import serializers
from .models import AtaFolder, AtaFile

class AtaFileSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField(read_only=True)
    size_human = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = AtaFile
        fields = ["id", "original_name", "file", "file_url", "size_human", "uploaded_at"]
        read_only_fields = ["id", "file", "file_url", "size_human", "uploaded_at"]

    def get_file_url(self, obj: AtaFile):
        request = self.context.get("request")
        if not obj.file:
            return None
        return request.build_absolute_uri(obj.file.url) if request else obj.file.url

    def get_size_human(self, obj: AtaFile):
        if not obj.file:
            return None

        try:
            size = obj.file.size  
        except Exception:
            return None

        if size is None:
            return None

        units = ["B", "KB", "MB", "GB", "TB", "PB"]
        value = float(size)

        for unit in units:
            if value < 1024 or unit == units[-1]:
                if unit == "B":
                    return f"{int(value)} {unit}"
                return f"{value:.1f} {unit}"
            value /= 1024

        return None


class AtaFolderSerializer(serializers.ModelSerializer):
    owner_id = serializers.IntegerField(source="owner.id", read_only=True)
    files = AtaFileSerializer(many=True, read_only=True)

    class Meta:
        model = AtaFolder
        fields = ["id", "name", "owner_id", "files", "created_at", "updated_at"]
        read_only_fields = ["id", "owner_id", "files", "created_at", "updated_at"]

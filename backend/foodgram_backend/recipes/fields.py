import base64
from django.core.files.base import ContentFile
from rest_framework import serializers


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith("data:image"):
            try:
                format, imgstr = data.split(";base64,")
                ext = format.split("/")[-1]
                data = base64.b64decode(imgstr)
                file_name = f"image.{ext}"
                data = ContentFile(data, name=file_name)
                return super().to_internal_value(data)
            except (ValueError, base64.binascii.Error):
                raise serializers.ValidationError("Неверный код изображения")
        return super().to_internal_value(data)

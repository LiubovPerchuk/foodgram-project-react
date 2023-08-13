import re

from django.core.exceptions import ValidationError


def hex_color_validator(value):
    """Метод валидации для поля color."""
    pattern = r'^#[0-9a-fA-F]{6}$'
    if not re.match(pattern, value):
        raise ValidationError("Неверный цветовой HEX-код")

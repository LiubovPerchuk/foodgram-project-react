import re
from django.core.exceptions import ValidationError


def hex_color_validator(value):
    """Метод валидации для поля color."""
    pattern = r'^#[0-9a-fA-F]{6}$'
    if not re.match(pattern, value):
        raise ValidationError("Неверный цветовой HEX-код")


def validate_amount(value):
    """Метод валидации для полей cooking_time и amount."""
    if value < 1:
        raise ValidationError("Значение должно быть больше 0!")

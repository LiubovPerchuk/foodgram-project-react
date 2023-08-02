from django.core.exceptions import ValidationError


def hex_color_validator(value):
    if not value.startswith("#") or not all(c in "0123456789abcdefABCDEF"
                                            for c in value[1:]):
        raise ValidationError("Неверный цветовой HEX-код")


def validate_amount(value):
    if value < 1:
        raise ValidationError("Значение должно быть больше 0!")

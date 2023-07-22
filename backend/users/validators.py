from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError


def validate_username(value):
    username_validator = UnicodeUsernameValidator()
    try:
        username_validator(value)
    except ValidationError:
        raise ValidationError("Некорректное имя пользователя.")

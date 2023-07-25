from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError


def validate_username(value):
    if value == "me":
        raise ValidationError("Обмануть меня вздумал? :)")

    username_validator = UnicodeUsernameValidator()
    try:
        username_validator(value)
    except ValidationError:
        raise ValidationError("Некорректное имя пользователя.")

# Учитель, не было проверки на me. Не могли создать,
# потому что такой юзер уже был создан я думаю. :)

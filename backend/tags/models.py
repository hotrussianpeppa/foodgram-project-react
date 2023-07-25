from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models


class Tag(models.Model):
    name = models.CharField(
        'Имя',
        max_length=settings.REPEATING_DIGIT,
        unique=True
    )
    color = models.CharField(
        'Цвет',
        max_length=7,
        unique=True,
        validators=[RegexValidator('^#([A-Fa-f0-9]{3}){1,2}$')]
    )
    slug = models.SlugField(
        'Слаг',
        max_length=settings.REPEATING_DIGIT,
        unique=True
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name

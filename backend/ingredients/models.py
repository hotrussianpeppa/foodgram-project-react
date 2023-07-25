from django.conf import settings
from django.db import models


class Ingredient(models.Model):
    name = models.CharField(
        'Имя',
        max_length=settings.REPEATING_DIGIT,
    )
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=settings.REPEATING_DIGIT,
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name

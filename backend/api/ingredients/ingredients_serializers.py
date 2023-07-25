from rest_framework import serializers

from ingredients.models import Ingredient
from recipes.models import RecipeIngredient


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с ингредиентами."""
    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientGetSerializer(serializers.ModelSerializer):
    """
    Сериализатор для получения информации об ингредиентах.

    Используется при работе с рецептами.
    """
    id = serializers.IntegerField(source='ingredient.id', read_only=True)
    name = serializers.CharField(source='ingredient.name', read_only=True)
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit',
        read_only=True
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class IngredientPostSerializer(serializers.ModelSerializer):
    """
    Сериализатор для добавления ингредиентов.

    Используется при работе с рецептами.
    """
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


# Учитель, поправил всё вроде бы.
# Так я кайфанул с этой работы, тяжело, но
# смотрю сейчас и так доволен результатом.
# Спасибо огромное!!! Кайфую вообще.
# Не зря всем говорил, что у меня ревьюер лучший
# Все 9 месяцев!!!
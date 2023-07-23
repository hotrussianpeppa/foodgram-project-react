from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from django.db import transaction

from api.users_serializers import RecipeSmallSerializer, UserGetSerializer
from api.utils import Base64ImageField, create_ingredients
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag,)


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с ингредиентами."""
    class Meta:
        model = Ingredient
        fields = '__all__'


class TagSerialiser(serializers.ModelSerializer):
    """Сериализатор для работы с тегами."""
    class Meta:
        model = Tag
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


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор для работы со списком покупок."""
    class Meta:
        model = ShoppingCart
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=('user', 'recipe'),
                message='Рецепт уже добавлен в список покупок'
            )
        ]

    def to_representation(self, instance):
        request = self.context.get('request')
        return RecipeSmallSerializer(
            instance.recipe,
            context={'request': request}
        ).data


class RecipeGetSerializer(serializers.ModelSerializer):
    """Сериализатор для получения информации о рецепте."""
    tags = TagSerialiser(many=True, read_only=True)
    author = UserGetSerializer(read_only=True)
    ingredients = IngredientGetSerializer(
        many=True, read_only=True,
        source='recipeingredients'
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField(required=False)

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'is_favorited', 'is_in_shopping_cart', 'name',
            'image', 'text', 'cooking_time'
        )

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        return (request and request.user.is_authenticated
                and Favorite.objects.filter(
                    user=request.user, recipe=obj
                ).exists())

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        return (request and request.user.is_authenticated
                and ShoppingCart.objects.filter(
                    user=request.user, recipe=obj
                ).exists())


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для добаления/обновления рецепта."""
    ingredients = IngredientPostSerializer(
        many=True, source='recipeingredients'
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'ingredients', 'tags', 'image',
            'name', 'text', 'cooking_time'
        )

    def validate(self, data):
        ingredients_list = []
        for ingredient in data.get('recipeingredients'):
            ingredients_list.append(ingredient.get('id'))
        if len(set(ingredients_list)) != len(ingredients_list):
            raise serializers.ValidationError(
                'Вы пытаетесь добавить в рецепт два одинаковых ингредиента'
            )
        return data

# Учитель, пытался поправить функцию по замечанию, но что бы я не делал, как бы
# не пытался, у меня переставала работать кнопка добавления рецептов,
# я уже и пачку перелистал всю и гугл перерыл и студентов спрашивал -
# никто не знает почему так... Ниже варианты решения оставил на всякий случай.
# Если можно, оставьте подсказку :)

    # def validate(self, data):
    #     ingredients = self.context.get('ingredient')
    #     if len(ingredients) <= 0:
    #         raise serializers.ValidationError(
    #             {'ingredients': ('Убедитесь, что хотя бы один '
    #                              'ингредиент добавлен')})
    #     ingredients_data = []
    #     for ingredient_item in ingredients:
    #         if ingredient_item['id'] in ingredients_data:
    #             raise serializers.ValidationError(
    #                 {'ingredient_item': (
    #                     'Убедитесь, что ингредиент не дублируется')})
    #         ingredients_data.append(ingredient_item['id'])
    #         if int(ingredient_item['amount']) <= 0:
    #             raise serializers.ValidationError({
    #                 'ingredients': ('Убедитесь, что значение количества '
    #                                 'ингредиента больше 0.')
    #             })
    #     return data

    # def validate_recipeingredients(self, recipeingredients):
    #     ingredients_list = []
    #     for ingredient in recipeingredients:
    #         ingredients_list.append(ingredient.get('id'))
    #     if len(set(ingredients_list)) != len(ingredients_list):
    #         raise serializers.ValidationError(
    #             'Вы пытаетесь добавить в рецепт два одинаковых ингредиента'
    #         )
    #     return recipeingredients

    # def validate(self, data):
    #     validated_data = super().validate(data)
    #     self.validate_recipeingredients(validated_data.get('recipeingredients'))
    #     return validated_data

    @transaction.atomic
    def create(self, validated_data):
        request = self.context.get('request')
        ingredients = validated_data.pop('recipeingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(author=request.user, **validated_data)
        recipe.tags.clear()
        recipe.tags.set(tags)
        create_ingredients(ingredients, recipe)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        ingredients = validated_data.pop('recipeingredients')
        tags = validated_data.pop('tags')
        instance.tags.clear()
        instance.tags.set(tags)
        instance.ingredients.clear()
        super().update(instance, validated_data)
        create_ingredients(ingredients, instance)
        instance.save()
        return instance

    def to_representation(self, instance):
        request = self.context.get('request')
        return RecipeGetSerializer(
            instance,
            context={'request': request}
        ).data


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с избранными рецептами."""
    class Meta:
        model = Favorite
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('user', 'recipe'),
                message='Рецепт уже добавлен в избранное'
            )
        ]

    def to_representation(self, instance):
        request = self.context.get('request')
        return RecipeSmallSerializer(
            instance.recipe,
            context={'request': request}
        ).data

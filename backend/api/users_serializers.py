from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import Recipe
from users.models import Subscription, User


# Понимаю, что данный класс логичнее было бы использовать в файле
# recipes_serializers.py и проще его импортировать сюда оттуда,
# но когда он был там, то я ловил ошибку циклического импорта...
# Находил решение в гугле, что проще закинуть этот класс в
# отдельный файл, но показалось, что это костыль
# и нелогичное решение проблемы. Сейчас вроде бы всё работает нормально.
class RecipeSmallSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с краткой информацией о рецепте."""
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class UserSignUpSerializer(UserCreateSerializer):
    """Сериализатор для регистрации пользователей."""
    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'password'
        )

    def validate_username(self, value):
        if value.lower() == 'me':
            raise serializers.ValidationError("Обмануть меня хочешь? :)")
        return value


class UserGetSerializer(UserSerializer):
    """Сериализатор для работы с информацией о пользователях."""
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed'
        )
        read_only_fields = 'is_subscribed',

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        return (request.user.is_authenticated
                and Subscription.objects.filter(
                    user=request.user, author=obj
                ).exists())


class UserSubscribeRepresentSerializer(UserGetSerializer):
    """"Сериализатор для предоставления информации
    о подписках пользователя.
    """
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed', 'recipes', 'recipes_count'
        )

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = request.GET.get('recipes_limit')

        recipes = (
            obj.recipes.all()[:int(recipes_limit)]
            if recipes_limit
            else obj.recipes.all()
        )
        return RecipeSmallSerializer(
            recipes, many=True,
            context={'request': request}
        ).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class UserSubscribeSerializer(serializers.ModelSerializer):
    """Сериализатор для подписки/отписки от пользователей."""
    class Meta:
        model = Subscription
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=('user', 'author'),
                message='Вы уже подписаны на этого пользователя'
            )
        ]

    def validate(self, data):
        request = self.context.get('request')
        if request.user == data['author']:
            raise serializers.ValidationError(
                'Нельзя подписываться на самого себя!'
            )
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        return UserSubscribeRepresentSerializer(
            instance.author, context={'request': request}
        ).data


# from djoser.serializers import UserCreateSerializer, UserSerializer
# from rest_framework import serializers
# from rest_framework.validators import UniqueTogetherValidator

# from recipes.models import Recipe
# from users.models import Subscription, User


# class UserSignUpSerializer(UserCreateSerializer):
#     """Сериализатор для регистрации пользователей."""
#     class Meta:
#         model = User
#         fields = (
#             'email', 'id', 'username', 'first_name',
#             'last_name', 'password'
#         )


# class UserGetSerializer(UserSerializer):
#     """Сериализатор для работы с информацией о пользователях."""
#     is_subscribed = serializers.ReadOnlyField()

#     class Meta:
#         model = User
#         fields = (
#             'email', 'id', 'username', 'first_name',
#             'last_name', 'is_subscribed'
#         )

#     def get_is_subscribed(self, obj):
#         request = self.context.get('request')
#         return (request.user.is_authenticated
#                 and Subscription.objects.filter(
#                     user=request.user, author=obj
#                 ).exists())


# # Понимаю, что данный класс логичнее было бы использовать в файле
# # recipes_serializers.py и проще его импортировать сюда оттуда,
# # но когда он был там, то я ловил ошибку циклического импорта...
# # Находил решение в гугле, что проще закинуть этот класс в
# # отдельный файл, но показалось, что это костыль
# # и нелогичное решение проблемы. Сейчас вроде бы всё работает нормально.
# class RecipeSmallSerializer(serializers.ModelSerializer):
#     """Сериализатор для работы с краткой информацией о рецепте."""
#     class Meta:
#         model = Recipe
#         fields = ('id', 'name', 'image', 'cooking_time')


# class UserSubscribeRepresentSerializer(UserGetSerializer):
#     """"Сериализатор для предоставления информации
#     о подписках пользователя.
#     """
#     is_subscribed = serializers.SerializerMethodField()
#     recipes = serializers.SerializerMethodField()
#     recipes_count = serializers.SerializerMethodField()

#     class Meta:
#         model = User
#         fields = (
#             'email', 'id', 'username', 'first_name',
#             'last_name', 'is_subscribed', 'recipes', 'recipes_count'
#         )

#     def get_recipes(self, obj):
#         request = self.context.get('request')
#         recipes_limit = request.query_params.get('recipes_limit')
#         if recipes_limit:
#             recipes = obj.recipes.all()[:int(recipes_limit)]
#         return RecipeSmallSerializer(
#             recipes, many=True,
#             context={'request': request}
#         ).data

#     def get_recipes_count(self, obj):
#         return obj.recipes.count()


# class UserSubscribeSerializer(serializers.ModelSerializer):
#     """Сериализатор для подписки/отписки от пользователей."""
#     class Meta:
#         model = Subscription
#         fields = '__all__'
#         validators = [
#             UniqueTogetherValidator(
#                 queryset=Subscription.objects.all(),
#                 fields=('user', 'author'),
#                 message='Вы уже подписаны на этого пользователя'
#             )
#         ]

#     def validate(self, data):
#         request = self.context.get('request')
#         if request.user == data['author']:
#             raise serializers.ValidationError(
#                 'Нельзя подписываться на самого себя!'
#             )
#         return data

#     def to_representation(self, instance):
#         request = self.context.get('request')
#         return UserSubscribeRepresentSerializer(
#             instance.author, context={'request': request}
#         ).data

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated

from django.db.models import Sum
from django.shortcuts import HttpResponse, get_object_or_404

from api.filters import IngredientFilter, RecipeFilter
from api.permissions import IsAdminAuthorOrReadOnly
from api.recipes_serializers import (FavoriteSerializer, IngredientSerializer,
                                     RecipeCreateSerializer,
                                     RecipeGetSerializer,
                                     ShoppingCartSerializer, TagSerialiser,)
from api.utils import create_model_instance, delete_model_instance
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag,)


class RecipeViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с рецептами."""
    queryset = Recipe.objects.all()
    permission_classes = (IsAdminAuthorOrReadOnly, )
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        """Возвращает класс сериализатора в зависимости от действия."""
        if self.action in ('list', 'retrieve'):
            return RecipeGetSerializer
        return RecipeCreateSerializer

    @action(detail=True,
            methods=['post', 'delete'],
            permission_classes=[IsAuthenticated, ])
    def favorite(self, request, pk):
        """Добавляет или удаляет рецепт из избранного."""
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':
            return create_model_instance(request, recipe, FavoriteSerializer)

        if request.method == 'DELETE':
            error_message = 'У вас нет этого рецепта в избранном'
            return delete_model_instance(
                request, Favorite,
                recipe, error_message
            )

    @action(detail=True,
            methods=['post', 'delete'],
            permission_classes=[IsAuthenticated, ])
    def shopping_cart(self, request, pk):
        """Добавляет или удаляет рецепт из списка покупок."""
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':
            return create_model_instance(
                request, recipe,
                ShoppingCartSerializer
            )

        if request.method == 'DELETE':
            error_message = 'У вас нет этого рецепта в списке покупок'
            return delete_model_instance(
                request, ShoppingCart,
                recipe, error_message
            )

    @action(detail=False,
            methods=['get'],
            permission_classes=[IsAuthenticated, ])
    def download_shopping_cart(self, request):
        """Скачивает список покупок в виде текстового файла."""
        ingredients = RecipeIngredient.objects.filter(
            recipe__carts__user=request.user
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(ingredient_amount=Sum('amount'))
        shopping_list = ['Список покупок:\n']
        for ingredient in ingredients:
            name = ingredient['ingredient__name']
            unit = ingredient['ingredient__measurement_unit']
            amount = ingredient['ingredient_amount']
            shopping_list.append(f'\n{name} - {amount}, {unit}')
        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = \
            'attachment; filename="shopping_cart.txt"'
        return response


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Отображение инфо о теге."""
    queryset = Tag.objects.all()
    serializer_class = TagSerialiser
    permission_classes = (AllowAny, )
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Класс представления об ингредиентах."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny, )
    filter_backends = (DjangoFilterBackend, )
    filterset_class = IngredientFilter
    pagination_class = None


# from django_filters.rest_framework import DjangoFilterBackend
# from rest_framework import mixins, viewsets
# from rest_framework.decorators import action
# from rest_framework.permissions import AllowAny, IsAuthenticated

# from django.db.models import Sum
# from django.shortcuts import HttpResponse, get_object_or_404

# from .recipes_serializers import (FavoriteSerializer, IngredientSerializer,
#                                RecipeCreateSerializer, RecipeGetSerializer,
#                                 ShoppingCartSerializer, TagSerialiser,)
# from api.filters import IngredientFilter, RecipeFilter
# from api.permissions import IsAdminAuthorOrReadOnly
# from api.utils import create_model_instance, delete_model_instance
# from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
#                             ShoppingCart, Tag,)


# class TagViewSet(viewsets.ReadOnlyModelViewSet):
#     """Отображение инфо о теге."""
#     queryset = Tag.objects.all()
#     serializer_class = TagSerialiser
#     permission_classes = (AllowAny, )
#     pagination_class = None


# class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
#     """Класс представления об ингредиентах."""
#     queryset = Ingredient.objects.all()
#     serializer_class = IngredientSerializer
#     permission_classes = (AllowAny, )
#     filter_backends = (DjangoFilterBackend, )
#     filterset_class = IngredientFilter
#     pagination_class = None


# class RecipeViewSet(mixins.CreateModelMixin,
#                     mixins.ListModelMixin,
#                     mixins.RetrieveModelMixin,
#                     mixins.UpdateModelMixin,
#                     mixins.DestroyModelMixin,
#                     viewsets.GenericViewSet):
#     """ViewSet для работы с рецептами."""
#     queryset = Recipe.objects.all()
#     permission_classes = (IsAdminAuthorOrReadOnly, )
#     filter_backends = (DjangoFilterBackend,)
#     filterset_class = RecipeFilter

#     def partial_update(self, request, *args, **kwargs):
#         """Частичное обновление рецепта."""
#         kwargs['partial'] = True
#         return self.update(request, *args, **kwargs)

#     def get_serializer_class(self):
#         """Возвращает класс сериализатора в зависимости от действия."""
#         if self.action in ('list', 'retrieve'):
#             return RecipeGetSerializer
#         return RecipeCreateSerializer

#     @action(detail=True,
#             methods=['post'],
#             permission_classes=[IsAuthenticated, ])
#     def add_to_favorite(self, request, pk):
#         """Добавляет рецепт в избранное."""
#         recipe = get_object_or_404(Recipe, id=pk)
#         return create_model_instance(request, recipe, FavoriteSerializer)

#     @action(detail=True,
#             methods=['delete'],
#             permission_classes=[IsAuthenticated, ])
#     def remove_from_favorite(self, request, pk):
#         """Удаляет рецепт из избранного."""
#         recipe = get_object_or_404(Recipe, id=pk)
#         error_message = 'У вас нет этого рецепта в избранном'
#     return delete_model_instance(request, Favorite, recipe, error_message)

#     @action(detail=True,
#             methods=['post'],
#             permission_classes=[IsAuthenticated, ])
#     def add_to_shopping_cart(self, request, pk):
#         """Добавляет рецепт в список покупок."""
#         recipe = get_object_or_404(Recipe, id=pk)
#         return create_model_instance(
#             request, recipe,
#             ShoppingCartSerializer
#         )

#     @action(detail=True,
#             methods=['delete'],
#             permission_classes=[IsAuthenticated, ])
#     def remove_from_shopping_cart(self, request, pk):
#         """Удаляет рецепт из списка покупок."""
#         recipe = get_object_or_404(Recipe, id=pk)
#         error_message = 'У вас нет этого рецепта в списке покупок'
#         return delete_model_instance(
#             request, ShoppingCart,
#             recipe, error_message
#         )

#     @action(detail=False,
#             methods=['get'],
#             permission_classes=[IsAuthenticated, ])
#     def download_shopping_cart(self, request):
#         """Скачивает список покупок в виде текстового файла."""
#         ingredients = self.get_shopping_list(request)
#         shopping_list = self.create_shopping_list(ingredients)
#         response = self.generate_shopping_list_response(shopping_list)
#         return response

#     def get_shopping_list(self, request):
#         """Получает список покупок."""
#         ingredients = RecipeIngredient.objects.filter(
#             recipe__carts__user=request.user
#         ).values(
#             'ingredient__name', 'ingredient__measurement_unit'
#         ).annotate(ingredient_amount=Sum('amount'))
#         return ingredients

#     def create_shopping_list(self, ingredients):
#         """Создаёт список покупок."""
#         shopping_list = ['Список покупок:\n']
#         for ingredient in ingredients:
#             name = ingredient['ingredient__name']
#             unit = ingredient['ingredient__measurement_unit']
#             amount = ingredient['ingredient_amount']
#             shopping_list.append(f'\n{name} - {amount}, {unit}')
#         return shopping_list

#     def generate_shopping_list_response(self, shopping_list):
#     """Генерирует HTTP-ответ со списком покупок в виде текстового файла."""
#         response = HttpResponse(shopping_list, content_type='text/plain')
#         response[
#             'Content-Disposition'
#         ] = 'attachment; filename="shopping_cart.txt"'
#         return response

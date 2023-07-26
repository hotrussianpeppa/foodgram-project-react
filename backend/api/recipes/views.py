from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django.db.models import Sum
from django.shortcuts import HttpResponse, get_object_or_404

from .mixins import PatchModelMixin
from api.recipes.serializers import (
    FavoriteSerializer,
    RecipeCreateSerializer,
    RecipeGetSerializer,
)
from api.shoppingcart.serializers import ShoppingCartSerializer
from api.utils.filters import RecipeFilter
from api.utils.permissions import IsAdminAuthorOrReadOnly
from recipes.models import Recipe, RecipeIngredient


class RecipeViewSet(mixins.CreateModelMixin,
                    mixins.ListModelMixin,
                    mixins.RetrieveModelMixin,
                    PatchModelMixin,
                    mixins.DestroyModelMixin,
                    viewsets.GenericViewSet):
    """ViewSet для работы с рецептами."""
    queryset = Recipe.objects.all()
    permission_classes = (IsAdminAuthorOrReadOnly, )
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        """Возвращает класс сериализатора в зависимости от действия."""
        if self.action in ('list', 'retrieve'):
            return RecipeGetSerializer
        return RecipeCreateSerializer

    def action_delete(self, pk, serializer_class):
        """
        Метод для удаления.

        Общий метод для удаления объекта
        из коллекции (избранное/список покупок).
        """
        user = self.request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        object = serializer_class.Meta.model.objects.filter(
            user=user,
            recipe=recipe
        )
        if self.request.method == 'DELETE':
            if not object.exists():
                return Response(
                    {'error': 'У вас нет этого рецепта где-либо :).'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        object.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def action_post(self, pk, serializer_class):
        """
        Метод для добавления.

        Общий метод для добавления объекта
        в коллекцию (избранное/список покупок).
        """
        user = self.request.user
        serializer = serializer_class(
            data={'user': user.id, 'recipe': pk},
            context={'request': self.request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    @action(
        methods=['POST'], detail=True,
        permission_classes=[permissions.IsAuthenticated]
    )
    def favorite(self, request, pk=None):
        """Добавляет рецепт в избранное."""
        return self.action_post(pk, FavoriteSerializer)

    @favorite.mapping.delete
    def favorite_delete(self, request, pk=None):
        """Удаляет рецепт из избранного."""
        return self.action_delete(pk, FavoriteSerializer)

    @action(
        methods=['POST'], detail=True,
        permission_classes=[permissions.IsAuthenticated]
    )
    def shopping_cart(self, request, pk=None):
        """Добавляет рецепт в список покупок."""
        return self.action_post(pk, ShoppingCartSerializer)

    @shopping_cart.mapping.delete
    def shopping_cart_delete(self, request, pk=None):
        """Удаляет рецепт из списка покупок."""
        return self.action_delete(pk, ShoppingCartSerializer)

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

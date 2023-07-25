from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from api.ingredients.ingredients_serializers import IngredientSerializer
from api.utils.filters import IngredientFilter
from recipes.models import Ingredient


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Класс представления об ингредиентах."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny, )
    filter_backends = (DjangoFilterBackend, )
    filterset_class = IngredientFilter
    pagination_class = None

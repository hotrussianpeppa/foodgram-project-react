from rest_framework.routers import DefaultRouter

from django.urls import include, path

from api.ingredients.ingredients_views import IngredientViewSet
from api.recipes.recipes_views import RecipeViewSet
from api.tags.tags_views import TagViewSet
from api.users.users_views import UserSubscribeView, UserSubscriptionsViewSet

v1_router = DefaultRouter()

v1_router.register(r'tags', TagViewSet, basename='tags')
v1_router.register(r'ingredients', IngredientViewSet, basename='ingredients')
v1_router.register(r'recipes', RecipeViewSet, basename='recipes')


urlpatterns = [
    path(
        'users/subscriptions/',
        UserSubscriptionsViewSet.as_view({'get': 'list'})
    ),
    path('users/<int:user_id>/subscribe/', UserSubscribeView.as_view()),
    path('', include(v1_router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]

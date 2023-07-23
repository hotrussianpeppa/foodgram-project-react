from rest_framework.routers import DefaultRouter

from django.urls import include, path

from api.recipes_views import IngredientViewSet, RecipeViewSet, TagViewSet
from api.users_views import UserSubscribeView, UserSubscriptionsViewSet

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

from rest_framework import mixins, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from django.shortcuts import get_object_or_404

from api.users_serializers import (UserSubscribeRepresentSerializer,
                                   UserSubscribeSerializer,)
from users.models import Subscription, User


class UserSubscribeView(APIView):
    """Класс, отвечающий за подписку пользователя на автора."""
    def post(self, request, user_id):
        """
        Метод, выполняющий подписку пользователя на автора
        """
        author = get_object_or_404(User, id=user_id)
        serializer = UserSubscribeSerializer(
            data={'user': request.user.id, 'author': author.id},
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, user_id):
        """Метод, выполняющий отписку пользователя от автора."""
        author = get_object_or_404(User, id=user_id)
        if not Subscription.objects.filter(
            user=request.user,
            author=author
        ).exists():
            return Response(
                {'errors': 'Вы не подписаны на этого пользователя'},
                status=status.HTTP_400_BAD_REQUEST
            )
        Subscription.objects.get(
            user=request.user.id,
            author=user_id
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserSubscriptionsViewSet(
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    """Класс возвращает подписчиков пользователя."""
    serializer_class = UserSubscribeRepresentSerializer

    def get_queryset(self):
        return User.objects.filter(following__user=self.request.user)

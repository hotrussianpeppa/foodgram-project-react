from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from .serializers import TagSerialiser
from tags.models import Tag


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Отображение инфо о теге."""
    queryset = Tag.objects.all()
    serializer_class = TagSerialiser
    permission_classes = (AllowAny, )
    pagination_class = None

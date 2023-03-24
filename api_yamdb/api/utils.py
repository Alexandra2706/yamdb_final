from django.shortcuts import get_object_or_404
from rest_framework import serializers, viewsets
from rest_framework.filters import SearchFilter
from rest_framework.mixins import (CreateModelMixin, DestroyModelMixin,
                                   ListModelMixin)
from rest_framework.viewsets import GenericViewSet

from .permissions import (IsAdminModeratorAuthorOrReadOnly, IsAdminOrReadOnly)
from reviews.models import Review, Title


class ReviewComment(viewsets.ModelViewSet):
    permission_classes = (IsAdminModeratorAuthorOrReadOnly,)
    _model = None
    _id = None

    def get_queryset(self):
        obj_id = self.kwargs.get(self._id)
        obj = get_object_or_404(self._model, id=obj_id)
        if self._model == Review:
            new_queryset = obj.comments.all()
            return new_queryset
        elif self._model == Title:
            new_queryset = obj.review.all()
            return new_queryset

    def perform_create(self, serializer):
        obj_id = self.kwargs.get(self._id)
        if self._model == Review:
            review = get_object_or_404(self._model, id=obj_id)
            serializer.save(author=self.request.user, review=review)
        elif self._model == Title:
            title = get_object_or_404(self._model, id=obj_id)
            serializer.save(author=self.request.user, title=title)


class CategoryGenre(CreateModelMixin, ListModelMixin,
                    DestroyModelMixin, GenericViewSet):
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class GenreCategorySerializer(serializers.ModelSerializer):
    """Класс сериализатор категории."""

    class Meta:
        fields = ('name', 'slug')
        lookup_field = 'slug'

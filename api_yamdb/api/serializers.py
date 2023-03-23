import datetime
import re

from django.shortcuts import get_object_or_404
from rest_framework import serializers

from reviews.models import User, Category, Title, Genre, Comments, Review
from .utils import GenreCategorySerializer


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор пользователя для админа"""

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name',
                  'bio', 'role')

    def validate_username(self, value):
        if not re.match(r'^[\w.@+-]+$', value):
            raise serializers.ValidationError('измените имя пользователя')
        return value


class ForUserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField(max_length=254)
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name',
                  'bio', 'role')

        read_only_fields = ['role']

    def validate_username(self, value):
        if not re.match(r'^[\w.@+-]+$', value):
            raise serializers.ValidationError('измените имя пользователя')
        return value


class CategorySerializer(GenreCategorySerializer):
    """Класс сериализатор категории."""

    class Meta(GenreCategorySerializer.Meta):
        model = Category


class GenreSerializer(GenreCategorySerializer):
    """Класс сериализатор жанра."""

    class Meta(GenreCategorySerializer.Meta):
        model = Genre


class TitleSerializer(serializers.ModelSerializer):
    """Класс сериализатор произведения"""
    name = serializers.CharField(max_length=256)
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug')
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        many=True,
        slug_field='slug')
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        fields = ('id', 'name', 'year', 'rating',
                  'description', 'genre', 'category')
        model = Title

    def validate_year(self, value):
        if value > int(datetime.datetime.now().year):
            raise serializers.ValidationError(
                'Год выпуска не может быть больше текущего!')
        return value


class TitleSerializerGet(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(read_only=True, many=True)
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        fields = ('id', 'name', 'year', 'rating',
                  'description', 'genre', 'category')
        model = Title


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор модели User."""
    title = serializers.SlugRelatedField(
        slug_field='name',
        read_only=True
    )
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    def validate(self, data):
        """Валидация для отзыва."""
        request = self.context['request']
        title_id = self.context['view'].kwargs.get('title_id')
        if request.method == 'POST' and Review.objects.filter(
                title=get_object_or_404(Title, id=title_id),
                author=request.user).exists():
            raise serializers.ValidationError(
                'Пользователь может оставить только один отзыв.')
        return data

    class Meta:
        fields = '__all__'
        model = Review


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для комментария."""
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        fields = ('id', 'text', 'pub_date', 'author', 'review')
        model = Comments
        read_only_fields = ('review',)


class UserRegistrationSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField(max_length=254)

    class Meta:
        model = User
        fields = ('username', 'email')

    def validate_username(self, value):
        if value.lower() == 'me':
            raise serializers.ValidationError(
                'Использовать имя "me" в качестве "username" запрещено')
        if not re.match(r'^[\w.@+-]+$', value):
            raise serializers.ValidationError('недопустимое имя пользователя')
        return value

    def validate(self, data):
        """Валидация пользователей."""
        username = data['username']
        email = data['email']
        if User.objects.filter(username=username, email=email).exists():
            return data
        elif User.objects.filter(username=username).exists():
            raise serializers.ValidationError(
                'Пользователь с таким именем уже существует')
        elif User.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                'Такой email уже используется')
        return data


class TokenSerializer(serializers.Serializer):
    confirmation_code = serializers.CharField()
    username = serializers.CharField()

    class Meta:
        model = User
        fields = ('username', 'confirmation_code',)

    def validate_username(self, value):
        if not re.match(r'^[\w.@+-]+$', value):
            raise serializers.ValidationError('измените имя пользователя')
        return value

from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.filters import SearchFilter
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from reviews.models import Category, Genre, Review, Title, User

from .permissions import IsAdminOnly, IsAdminOrReadOnly
from .serializers import (CategorySerializer, CommentSerializer,
                          ForUserSerializer, GenreSerializer,
                          ReviewSerializer, TitleSerializer,
                          TitleSerializerGet, TokenSerializer,
                          UserRegistrationSerializer, UserSerializer)
from .utils import CategoryGenre, ReviewComment


class UsersViewSet(viewsets.ModelViewSet):
    """Получение списка пользователей и редактирование."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdminOnly,)
    filter_backends = (SearchFilter,)
    lookup_field = 'username'
    search_fields = ['username']
    pagination_class = LimitOffsetPagination
    http_method_names = ['get', 'post', 'patch', 'delete']

    @action(
        methods=['GET', 'PATCH'],
        detail=False,
        permission_classes=(IsAuthenticated,),
        url_path='me',
        url_name='current_user_info')
    def get_current_user_info(self, request, ):
        """Просмотр и редактирование своего аккаунта."""
        if request.method == 'GET':
            serializer = ForUserSerializer(request.user)
            return Response(serializer.data)
        serializer = ForUserSerializer(
            request.user, data=request.data, partial=True,
        )
        if serializer.is_valid():
            serializer.save(role=request.user.role)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryViewSet(CategoryGenre):
    """ Получить список всех категорий. Права доступа: Доступно без токена"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(CategoryGenre):
    """
    Получить список всех жанров. Права доступа: Доступно без токена
    """
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    serializer_class = TitleSerializerGet
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_field = ('genre', 'category')

    def get_serializer_class(self):
        if self.request.method in ('GET', 'HEAD', 'OPTIONS'):
            return TitleSerializerGet
        return TitleSerializer

    def get_queryset(self):
        queryset = Title.objects.annotate(rating=Avg('review__score'))
        genre = self.request.query_params.get('genre')
        category = self.request.query_params.get('category')
        year = self.request.query_params.get('year')
        name = self.request.query_params.get('name')
        if genre:
            queryset = queryset.filter(genre__slug=genre)
        if category:
            queryset = queryset.filter(category__slug=category)
        if year:
            queryset = queryset.filter(year=year)
        if name:
            queryset = queryset.filter(name=name)
        return queryset


class CommentViewSet(ReviewComment):
    serializer_class = CommentSerializer

    _model = Review
    _id = 'review_id'


class ReviewViewSet(ReviewComment):
    """Просмотр и редактирование рецензий."""
    serializer_class = ReviewSerializer

    _model = Title
    _id = 'title_id'


@api_view(['POST'])
@permission_classes([AllowAny])
def user_registration(request):
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        username = serializer.validated_data.get('username')
        email = serializer.validated_data.get('email')
        user, created = User.objects.get_or_create(username=username,
                                                   email=email)
        confirmation_code = default_token_generator.make_token(user)
        send_mail('код подтверждения', confirmation_code,
                  None, [serializer.validated_data['email']],
                  fail_silently=False, )
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def get_tokens_for_user(request):
    serializer = TokenSerializer(data=request.data)
    if serializer.is_valid():
        user = get_object_or_404(User,
                                 username=serializer.validated_data[
                                     'username'])
        if default_token_generator.check_token(
                user, serializer.validated_data['confirmation_code']):
            token = RefreshToken.for_user(user)
            return Response({'token': str(token.access_token)},
                            status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

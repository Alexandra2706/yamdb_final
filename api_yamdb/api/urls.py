from django.urls import include, path
from rest_framework import routers

from . import views
from .views import (CategoryViewSet, GenreViewSet, UsersViewSet,
                    TitleViewSet, CommentViewSet, ReviewViewSet)

v1_router = routers.DefaultRouter()
v1_router.register('categories', CategoryViewSet, basename='categories')
v1_router.register('genres', GenreViewSet, basename='genres')
v1_router.register('titles', TitleViewSet, basename='titles')
v1_router.register('users', UsersViewSet, basename='users')
v1_router.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='reviews',
)
v1_router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comments',
)

urlpatterns = [
    path('v1/auth/signup/', views.user_registration, name='user_registration'),
    path('v1/auth/token/', views.get_tokens_for_user, name='get_token'),
    path('v1/', include(v1_router.urls)),
]

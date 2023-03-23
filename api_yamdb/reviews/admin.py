from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, Category, Genre, Title, Review, Comments


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'slug',
    )
    list_editable = ('slug',)
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-пусто-'


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'slug',
    )
    list_editable = ('slug',)
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-пусто-'


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'year',
        'category',
    )
    list_editable = ('name', 'year',)
    search_fields = ('name',)
    list_filter = ('category',)
    empty_value_display = '-пусто-'


@admin.register(Comments)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'review',
        'text',
        'author',
        'pub_date',
    )
    search_fields = ('text', 'author',)
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'title',
        'text',
        'author',
        'score',
        'pub_date',
    )
    search_fields = ('text', 'author',)
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'


admin.site.register(User, UserAdmin)

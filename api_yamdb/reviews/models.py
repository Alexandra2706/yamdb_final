from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Roles(models.TextChoices):
    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'


class User(AbstractUser):
    first_name = models.CharField(
        max_length=150,
        verbose_name='Firstname',
        null=True)
    last_name = models.CharField(
        max_length=150,
        verbose_name='Lastname',
        null=True)
    username = models.CharField(
        max_length=150,
        verbose_name='Username',
        unique=True
    )
    bio = models.TextField(null=True)
    email = models.EmailField(
        verbose_name='Email',
        unique=True,
        max_length=254
    )
    role = models.CharField(
        max_length=20,
        choices=Roles.choices,
        default=Roles.USER,

    )

    def __str__(self):
        return f'{self.username}'

    @property
    def is_admin(self):
        return (self.role == Roles.ADMIN
                or self.is_superuser
                or self.is_staff)

    @property
    def is_moderator(self):
        return self.role == Roles.MODERATOR


class Category(models.Model):
    name = models.CharField(
        max_length=30,
        verbose_name='Название категории',
    )
    slug = models.SlugField(
        unique=True,
        max_length=20,
        verbose_name='slug-значение категории'
    )

    def __str__(self):
        return f'{self.name}'


class Genre(models.Model):
    name = models.CharField(
        max_length=30,
        verbose_name='Жанр',
    )
    slug = models.SlugField(
        unique=True,
        max_length=20,
        verbose_name='slug-значение жанра'
    )

    def __str__(self):
        return f'{self.name}'


class Title(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='Название произведения',
    )
    year = models.IntegerField()
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='Текст комментария',
    )
    category = models.ForeignKey(
        Category,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='titles',
        verbose_name='Категория произведения')
    genre = models.ManyToManyField(Genre, through='GenreTitle', )

    def get_genre(self):
        return "\n".join([p.slug for p in self.genre.all()])

    def __str__(self):
        return f'{self.name} {self.category}'


class GenreTitle(models.Model):
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='title',
        verbose_name='Жанр произведения')
    genre = models.ForeignKey(
        Genre,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='genre',
        verbose_name='Жанр')

    def __str__(self):
        return f'{self.title} {self.genre}'


class Review(models.Model):
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='review',
        verbose_name='Произведение')
    text = models.TextField(
        verbose_name='Текст отзыва',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='review',
        verbose_name='Автор'
    )
    score = models.IntegerField(default=None,
                                validators=[MaxValueValidator(10),
                                            MinValueValidator(1)])
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = [
            models.UniqueConstraint(
                fields=('title', 'author',),
                name='unique review'
            )]
        ordering = ('-pub_date',)

    def __str__(self):
        return f'{self.author} {self.text}'


class Comments(models.Model):
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Комментарий ревью'
    )
    text = models.TextField(
        verbose_name='Текст комментария',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )

    def __str__(self):
        return f'{self.author} {self.text}'

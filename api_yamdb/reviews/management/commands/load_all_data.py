import csv

from django.core.management import BaseCommand
from reviews.models import (User, Category, Title, Genre,
                            Comments, Review, GenreTitle)


def iter_csv(file_path: str):
    with open(file_path, 'r', encoding="utf8") as inp_f:
        reader = csv.DictReader(inp_f)
        for row in reader:
            yield row


class Command(BaseCommand):
    def handle(self, *args, **options):
        reader = iter_csv('static/data/users.csv')
        for row in reader:
            user = User(id=row['id'], username=row['username'],
                        email=row['email'], role=row['role'],
                        bio=row['bio'],
                        first_name=row['first_name'],
                        last_name=row['last_name'])
            user.save()

        reader = iter_csv('static/data/category.csv')
        for row in reader:
            category = Category(id=row['id'], name=row['name'],
                                slug=row['slug'])
            category.save()

        reader = iter_csv('static/data/genre.csv')
        for row in reader:
            genre = Genre(id=row['id'], name=row['name'], slug=row['slug'])
            genre.save()

        reader = iter_csv('static/data/titles.csv')
        for row in reader:
            title = Title(id=row['id'], name=row['name'],
                          year=int(row['year']),
                          category=Category.objects.get(pk=row['category']),)
            title.save()

        reader = iter_csv('static/data/genre_title.csv')
        for row in reader:
            genre_title = GenreTitle(id=row['id'],
                                     title=Title.objects.get(
                                         pk=row['title_id']),
                                     genre=Genre.objects.get(
                                         pk=row['genre_id']), )
            genre_title.save()

        reader = iter_csv('static/data/review.csv')
        for row in reader:
            review = Review(id=row['id'],
                            title=Title.objects.get(pk=row['title_id']),
                            text=row['text'],
                            author=User.objects.get(pk=row['author']),
                            score=row['score'], pub_date=row['pub_date'])
            review.save()

        reader = iter_csv('static/data/comments.csv')
        for row in reader:
            comment = Comments(id=row['id'],
                               review=Review.objects.get(
                                   pk=row['review_id']),
                               text=row['text'],
                               author=User.objects.get(pk=row['author']),
                               pub_date=row['pub_date'])
            comment.save()

import pytest

from datetime import timedelta

from django.test.client import Client
from django.utils import timezone

from news.models import Comment, News


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='Пользователь')


@pytest.fixture
def author_client(author):
    return login_user(author)


@pytest.fixture
def not_author_client(not_author):
    return login_user(not_author)


def login_user(user):
    client = Client()
    client.force_login(user)
    return client


@pytest.fixture
def news():
    news = News.objects.create(
        title='Заголовок',
        text='Новость',
    )
    return news


@pytest.fixture
def comment(news, author):
    comment = Comment.objects.create(
        news=news,
        text='Комментарий',
        author=author
    )
    return comment


@pytest.fixture
def several_news():
    all_news = [
        News(
            title=f'Заголовок {i}',
            text=f'Новость {i}',
            date=timezone.now() - timedelta(days=i)
        )
        for i in range(11)
    ]
    return News.objects.bulk_create(all_news)


@pytest.fixture
def several_comments(news, author):
    for i in range(10):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Комментарий {i}',
        )
        comment.created = timezone.now() + timedelta(days=i)
        comment.save()


@pytest.fixture
def form_data():
    return {
        'text': 'Новый комментарий'
    }

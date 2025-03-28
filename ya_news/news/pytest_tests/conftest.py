from datetime import timedelta

import pytest
from django.conf import settings
from django.test.client import Client
from django.urls import reverse
from django.utils import timezone

from news.models import Comment, News


QUANTITY_NEWS = settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='Пользователь')


def login_user_client(user):
    client = Client()
    client.force_login(user)
    return client


@pytest.fixture
def author_client(author):
    return login_user_client(author)


@pytest.fixture
def not_author_client(not_author):
    return login_user_client(not_author)


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
        for i in range(QUANTITY_NEWS + 1)
    ]
    News.objects.bulk_create(all_news)


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
def news_home():
    return reverse('news:home')


@pytest.fixture
def users_login():
    return reverse('users:login')


@pytest.fixture
def users_logout():
    return reverse('users:logout')


@pytest.fixture
def users_signup():
    return reverse('users:signup')


@pytest.fixture
def news_detail(news):
    return reverse('news:detail', args=(news.id,))


@pytest.fixture
def comment_edit(comment):
    return reverse('news:edit', args=(comment.id,))


@pytest.fixture
def comment_delete(comment):
    return reverse('news:delete', args=(comment.id,))


@pytest.fixture
def redirect_comment_edit(users_login, comment_edit):
    return f'{users_login}?next={comment_edit}'


@pytest.fixture
def redirect_comment_delete(users_login, comment_delete):
    return f'{users_login}?next={comment_delete}'

import pytest
from django.conf import settings

from news.forms import CommentForm


QUANTITY_NEWS = settings.NEWS_COUNT_ON_HOME_PAGE

pytestmark = pytest.mark.django_db


def test_note_in_list_for_author(client, several_news, news_home):
    """Количество новостей на главной странице."""
    assert client.get(news_home).context['object_list'].count(
    ) == QUANTITY_NEWS


def test_news_order(client, several_news, news_home):
    """Новости отсортированы от самой свежей к самой старой."""
    all_dates = [
        news.date for news in client.get(news_home).context['object_list']
    ]
    assert all_dates == sorted(all_dates, reverse=True)


def test_comment_order(client, several_comments, news_detail):
    """Старые новости в начале списка, новые — в конце."""
    response = client.get(news_detail)
    assert 'news' in response.context
    news = response.context['news']
    all_dates = [comment.created for comment in news.comment_set.all()]
    assert all_dates == sorted(all_dates)


def test_comment_form_author(author_client, news_detail):
    """Форма комментария доступна авторизованному пользователю."""
    response = author_client.get(news_detail)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)


def test_comment_form_not_author(client, news_detail):
    """Форма комментария недоступна неавторизованному пользователю."""
    assert 'form' not in client.get(news_detail).context

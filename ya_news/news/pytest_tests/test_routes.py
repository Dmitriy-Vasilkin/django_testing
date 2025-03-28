from http import HTTPStatus as hs

import pytest
from pytest_django.asserts import assertRedirects
from pytest_lazyfixture import lazy_fixture as lf


ANONIM = lf('client')
AUTHOR = lf('author_client')
NOT_AUTHOR = lf('not_author_client')

OK = hs.OK
NOT_FOUND = hs.NOT_FOUND

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    'reverse_url, parametrized_client, http_status',
    (
        (lf('news_home'), ANONIM, OK),
        (lf('users_login'), ANONIM, OK),
        (lf('users_logout'), ANONIM, OK),
        (lf('users_signup'), ANONIM, OK),
        (lf('news_detail'), ANONIM, OK),
        (lf('comment_edit'), AUTHOR, OK),
        (lf('comment_delete'), AUTHOR, OK),
        (lf('comment_edit'), NOT_AUTHOR, NOT_FOUND),
        (lf('comment_delete'), NOT_AUTHOR, NOT_FOUND),
    )
)
def test_routes(reverse_url, parametrized_client, http_status):
    """Проверка доступности страниц."""
    response = parametrized_client.get(reverse_url)
    assert response.status_code == http_status


@pytest.mark.parametrize(
    'reverse_url, redirect_url',
    (
        (lf('comment_edit'), lf('redirect_comment_edit')),
        (lf('comment_delete'), lf('redirect_comment_delete')),
    )
)
def test_redirect(client, reverse_url, redirect_url):
    """Редактирование и удаление комментария анонимным пользователем."""
    response = client.get(reverse_url)
    assertRedirects(response, redirect_url)

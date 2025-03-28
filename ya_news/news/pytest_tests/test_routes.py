from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects


ANONIM = pytest.lazy_fixture('client')
AUTHOR = pytest.lazy_fixture('author_client')
NOT_AUTHOR = pytest.lazy_fixture('not_author_client')

OK = HTTPStatus.OK
NOT_FOUND = HTTPStatus.NOT_FOUND

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    'reverse_url, parametrized_client, http_status',
    (
        (pytest.lazy_fixture('news_home'), ANONIM, OK),
        (pytest.lazy_fixture('users_login'), ANONIM, OK),
        (pytest.lazy_fixture('users_logout'), ANONIM, OK),
        (pytest.lazy_fixture('users_signup'), ANONIM, OK),
        (pytest.lazy_fixture('news_detail'), ANONIM, OK),
        (pytest.lazy_fixture('comment_edit'), AUTHOR, OK),
        (pytest.lazy_fixture('comment_delete'), AUTHOR, OK),
        (pytest.lazy_fixture('comment_edit'), NOT_AUTHOR, NOT_FOUND),
        (pytest.lazy_fixture('comment_delete'), NOT_AUTHOR, NOT_FOUND),
    )
)
def test_routes(reverse_url, parametrized_client, http_status):
    """Проверка доступности страниц."""
    response = parametrized_client.get(reverse_url)
    assert response.status_code == http_status


@pytest.mark.parametrize(
    'reverse_url, redirect_url',
    (
        (
            pytest.lazy_fixture('comment_edit'),
            pytest.lazy_fixture('redirect_comment_edit')
        ),
        (
            pytest.lazy_fixture('comment_delete'),
            pytest.lazy_fixture('redirect_comment_delete')
        ),
    )
)
def test_redirect(client, reverse_url, redirect_url):
    """Редактирование и удаление комментария анонимным пользователем."""
    response = client.get(reverse_url)
    assertRedirects(response, redirect_url)

import pytest

from http import HTTPStatus

from django.urls import reverse

from pytest_django.asserts import assertRedirects


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name',
    ('news:home', 'users:login', 'users:logout', 'users:signup')
)
def test_pages_availability_for_anonymous(client, name):
    """Проверка доступности страниц для анонимного пользователя."""
    url = reverse(name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_news_availability_for_anonymous(client, news):
    """Страница отдельной новости доступна анонимному пользователю."""
    url = reverse('news:detail', args=(news.id,))
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


def test_comment_edit_availability_for_author(author_client, news, comment):
    """Редактирование комментария доступно автору комментария."""
    url = reverse('news:edit', args=(comment.id,))
    response = author_client.get(url)
    assert response.status_code == HTTPStatus.OK


def test_comment_delete_availability_for_author(author_client, news, comment):
    """Удаление комментария доступно автору комментария."""
    url = reverse('news:delete', args=(comment.id,))
    response = author_client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(

    'name, note_object',
    (
        ('news:edit', pytest.lazy_fixture('comment')),
        ('news:delete', pytest.lazy_fixture('comment')),

    ),
)
@pytest.mark.django_db
def test_del_and_edit_anonim(client, news, name, note_object):
    """Редактирование и удаление комментария анонимным пользователем."""
    login_url = reverse('users:login')
    if note_object is not None:
        url = reverse(name, args=(note_object.id,))
    else:
        url = reverse(name)
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)


@pytest.mark.parametrize(

    'name, note_object',
    (
        ('news:edit', pytest.lazy_fixture('comment')),
        ('news:delete', pytest.lazy_fixture('comment')),

    ),
)
def test_del_and_edit_not_author(not_author_client, news, name, note_object):
    """Редактирование и удаление не своих комментариев неавтором."""
    if note_object is not None:
        url = reverse(name, args=(note_object.id,))
    else:
        url = reverse(name)
    response = not_author_client.get(url)
    assert response.status_code == HTTPStatus.NOT_FOUND

import pytest

from http import HTTPStatus

from django.urls import reverse

from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, news, form_data):
    """Анонимный пользователь не может отправить комментарий."""
    url = reverse('news:detail', args=(news.id,))
    client.post(url, data=form_data)
    compare_comments_count(0)


def test_author_user_can_create_comment(author_client, news, form_data):
    """Авторизованный пользователь может отправить комментарий."""
    url = reverse('news:detail', args=(news.id,))
    response = author_client.post(url, data=form_data)
    assertRedirects(response, f'{url}#comments')
    compare_comments_count(1)


def test_cant_create_comment_with_bad_words(author_client, author, news):
    """Запрещенные слова не опубликуются, форма вернет ошибку."""
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    url = reverse('news:detail', args=(news.id,))
    response = author_client.post(url, data=bad_words_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    compare_comments_count(0)


def test_author_can_delete_comment(author_client, news, comment):
    """Авторизованный пользователь может удалять свои комментарии."""
    response = response_for_delete_comment(author_client, comment)
    compare_redirect_url(response, news)
    compare_comments_count(0)


def test_author_can_edit_comment(author_client, news, comment, form_data):
    """Авторизованный пользователь может редактировать свои комментарии."""
    response = response_for_edit_comment(author_client, comment)
    compare_redirect_url(response, news)
    assert comment.text == form_data['text']
    compare_comments_count(1)


def test_not_author_cant_delete_comment(not_author_client, news, comment):
    """Авторизованный пользователь не может удалять чужие комментарии."""
    response = response_for_delete_comment(not_author_client, comment)
    assert response.status_code == HTTPStatus.NOT_FOUND
    compare_comments_count(1)


def test_not_author_cant_edit_comment(
    not_author_client, news, comment, form_data
):
    """Авторизованный пользователь не может изменить чужие комментарии."""
    response = response_for_edit_comment(not_author_client, comment)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert comment.text != form_data['text']


def compare_comments_count(expected_result):
    """Сравнение кол-ва записей."""
    comments_count = Comment.objects.count()
    assert comments_count == expected_result


def response_for_edit_comment(user, obj):
    """Ответ на запрос редактирования и обновление записи."""
    new_comment = 'Новый комментарий'
    url_edit = reverse('news:edit', args=(obj.id,))
    response = user.post(url_edit, data={'text': new_comment})
    obj.refresh_from_db()
    return response


def response_for_delete_comment(user, obj):
    """Ответ на запрос удаления."""
    url_delete = reverse('news:delete', args=(obj.id,))
    return user.post(url_delete)


def compare_redirect_url(response, obj):
    """Сравнение url редиректа."""
    url = reverse('news:detail', args=(obj.id,)) + '#comments'
    assertRedirects(response, url)

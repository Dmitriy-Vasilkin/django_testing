from http import HTTPStatus

import pytest
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


FORM_DATA = {'text': 'Новый комментарий'}

pytestmark = pytest.mark.django_db


def test_anonymous_user_cant_create_comment(client, news_detail):
    """Анонимный пользователь не может отправить комментарий."""
    comments_count_start = Comment.objects.count()
    client.post(news_detail, data=FORM_DATA)
    assert comments_count_start == Comment.objects.count()


def test_author_user_can_create_comment(
    author, author_client, news, news_detail
):
    """Авторизованный пользователь может отправить комментарий."""
    Comment.objects.all().delete()
    response = author_client.post(news_detail, data=FORM_DATA)
    assertRedirects(response, f'{news_detail}#comments')
    assert Comment.objects.count() == 1
    comment = Comment.objects.get()
    assert comment.text == FORM_DATA['text']
    assert comment.news == news
    assert comment.author == author


def test_cant_create_comment_with_bad_words(author_client, news_detail):
    """Запрещенные слова не опубликуются, форма вернет ошибку."""
    comments_count_start = Comment.objects.count()
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = author_client.post(news_detail, data=bad_words_data)
    assert comments_count_start == Comment.objects.count()
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )


def test_author_can_delete_comment(
    author_client, comment, comment_delete, news_detail
):
    """Авторизованный пользователь может удалять свои комментарии."""
    comments_count_start = Comment.objects.count()
    response = author_client.post(comment_delete)
    assertRedirects(response, news_detail + '#comments')
    assert comments_count_start - 1 == Comment.objects.count()


def test_author_can_edit_comment(
    author, author_client, news, comment, comment_edit, news_detail
):
    """Авторизованный пользователь может редактировать свои комментарии."""
    new_comment = 'Новый комментарий'
    response = author_client.post(comment_edit, data={'text': new_comment})
    comment.refresh_from_db()
    assertRedirects(response, news_detail + '#comments')
    assert comment.text == FORM_DATA['text']
    assert comment.news == news
    assert comment.author == author


def test_not_author_cant_delete_comment(
    not_author_client, comment, comment_delete
):
    """Авторизованный пользователь не может удалять чужие комментарии."""
    comments_count_start = Comment.objects.count()
    response = not_author_client.post(comment_delete)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert comments_count_start == Comment.objects.count()


def test_not_author_cant_edit_comment(
    not_author_client, comment, comment_edit
):
    """Авторизованный пользователь не может изменить чужие комментарии."""
    new_comment = 'Новый комментарий'
    response = not_author_client.post(comment_edit, data={'text': new_comment})
    assert response.status_code == HTTPStatus.NOT_FOUND
    new_comment = Comment.objects.get(id=comment.id)
    assert new_comment.author == comment.author
    assert new_comment.news == comment.news
    assert new_comment.text == comment.text

from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

user = get_user_model()


class TestRoutes(TestCase):
    """
    Тестирование маршрутов.

    Методы:
        setUpTestData() - тестовые данные.
        test_pages_availability
            - маршруты доступны анонимному пользователю.
        test_redirect_for_anonymous_client()
            - тест редиректов для анонимного пользователя.
        test_availability_for_comment_and_delete()
            - тестирование доступности редактирования и удаления для
              анонимного пользоваиеля и автора.
        test_availability_for_login()
            - тестирование добавления, списка записей и страницы
              успешного сохранения для автора.
        compare_status_code()
            - сравнение статусов кодов.
    """

    @classmethod
    def setUpTestData(cls):
        cls.author = user.objects.create(username='Автор')
        cls.reader = user.objects.create(username='Аноним')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='slug',
            author=cls.author
        )

    def test_pages_availability(self):
        url_paths = (
            'notes:home', 'users:login', 'users:logout', 'users:signup'
        )
        self.compare_status_code(HTTPStatus.OK, url_paths)

    def test_redirect_for_anonymous_client(self):
        login_url = reverse('users:login')
        for name, args in (
            ('notes:list', None),
            ('notes:success', None),
            ('notes:add', None),
            ('notes:detail', (self.note.id,)),
            ('notes:edit', (self.note.id,)),
            ('notes:delete', (self.note.id,)),
        ):
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

    def test_availability_for_comment_and_delete(self):
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            url_paths = ('notes:edit', 'notes:delete', 'notes:detail')
            self.compare_status_code(status, url_paths, args=(self.note.slug,))

    def test_availability_for_login(self):
        self.client.force_login(self.author)
        url_paths = ('notes:add', 'notes:list', 'notes:success')
        self.compare_status_code(HTTPStatus.OK, url_paths)

    def compare_status_code(self, http_status, url_paths, args=None):
        for url_path in url_paths:
            with self.subTest():
                url = reverse(url_path, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, http_status)

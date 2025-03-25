from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

user = get_user_model()


class TestContent(TestCase):
    """
    Проверка контента.

    Методы:
        test_only_author_notes()
            - в список заметок попадают записи
              только одного пользователя.
        test_authorized_client_has_add_form()
            - на страницу добавления записи передается форма.
        test_authorized_client_has_edit_form()
            - на страницу редактирования записи передается форма.
        test_note_in_context()
            - отдельная заметка передаётся в словаре context.
        get_response()
            - получение ответа сервера.
    """

    @classmethod
    def setUpTestData(cls):
        cls.author = user.objects.create(username='Автор')
        cls.another_author = user.objects.create(username='Аноним')
        all_notes_author = [
            Note(
                title=f'Заголовок {index}',
                text='Просто текст.',
                slug=f'slug_{index}',
                author=cls.author
            )
            for index in range(5)
        ]
        Note.objects.bulk_create(all_notes_author)
        cls.note_another_author = Note.objects.create(
            title='Заголовок_1',
            text='Просто текст_1.',
            slug='slug_user_2',
            author=cls.another_author
        )

    def test_only_author_notes(self):
        response = self.get_response('notes:list')
        object_list = response.context['object_list']
        author_list = [note.author for note in object_list]
        self.assertEqual(len(set(author_list)), 1)

    def test_authorized_client_has_add_form(self):
        response = self.get_response('notes:add')
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)

    def test_authorized_client_has_edit_form(self):
        response = self.get_response(
            'notes:edit', (self.note_another_author.slug,)
        )
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)

    def test_note_in_context(self):
        response = self.get_response('notes:list')
        context = response.context['object_list']
        self.assertIn(self.note_another_author, context)

    def get_response(self, url, args=None):
        self.client.force_login(self.another_author)
        url = reverse(url, args=args)
        return self.client.get(url)

from .fixtures import Fixtures
from notes.forms import NoteForm


class TestContent(Fixtures):
    """
    Проверка контента.

    Методы:
        test_only_author_notes()
            - в список заметок попадают записи только одного пользователя.
        test_note_in_context()
            - отдельная заметка передаётся в словаре context.
        test_authorized_client_has_form()
            - на страницу добавления записи передается форма.
            - на страницу редактирования записи передается форма.
    """

    def test_only_author_notes(self):
        response = self.author_client.get(self.notes_list)
        author_notes = [
            note.author for note in response.context['object_list']
        ]
        self.assertEqual(len(set(author_notes)), 1)

    def test_note_in_context(self):
        response = self.author_client.get(self.notes_list)
        self.assertIn(self.author_note, response.context['object_list'])

    def test_authorized_client_has_form(self):
        url_paths = (
            self.notes_add,
            self.notes_edit,
        )
        for url_path in url_paths:
            with self.subTest(url_path=url_path):
                response = self.author_client.get(url_path)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)

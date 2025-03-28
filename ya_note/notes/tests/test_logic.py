from http import HTTPStatus

from django.contrib.auth import get_user
from pytils.translit import slugify

from .fixtures import Fixtures
from notes.forms import NoteForm, WARNING
from notes.models import Note


class TestLogic(Fixtures):
    """
    Проверка создания записи.

    Методы:
        test_anonymous_user_cant_create_note()
            - анонимный пользователь не может создать запись.
        test_user_can_create_note()
            - залогиненный пользователь может создать запись.
        test_impossible_equal_slug()
            - нельзя создать запись с одинаковым slug.
        test_create_slug_with_slugify()
            - применяется slugify при неуказанном slug.
        test_author_can_delete_note()
            - автор может удалять свои записи.
        test_user_cant_delete_note_of_another_user()
            - пользователь не иожет удалять чужие записи.
        test_author_can_edit_note()
            - автор может редактировать свои записи.
        test_user_cant_edit_note_of_another_user()
            - пользователь не иожет изменять чужие записи.
    """

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.form_data = {
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': 'slug',
        }
        cls.verification_slug = slugify(cls.form_data['title'])

    def test_anonymous_user_cant_create_note(self):
        notes_count_start = Note.objects.count()
        self.client.post(self.notes_add, data=self.form_data)
        self.assertEqual(notes_count_start, Note.objects.count())

    def test_user_can_create_note(self):
        Note.objects.all().delete()
        self.author_client.post(self.notes_add, data=self.form_data)
        self.assertEqual(Note.objects.count(), 1)
        check_note = Note.objects.get()
        self.assertEqual(check_note.title, self.form_data['title'])
        self.assertEqual(check_note.text, self.form_data['text'])
        self.assertEqual(check_note.author, get_user(self.author_client))
        self.assertEqual(check_note.slug, self.form_data['slug'])

    def test_impossible_equal_slug(self):
        notes_count_start = Note.objects.count()
        form = NoteForm(data=self.form_data)
        self.form_data['slug'] = self.author_note.slug
        self.assertFalse(form.is_valid())
        self.assertIn('slug', form.errors)
        response = self.author_client.post(self.notes_add, data=self.form_data)
        self.assertEqual(notes_count_start, Note.objects.count())
        self.assertFormError(
            response,
            form='form',
            field='slug',
            errors=self.author_note.slug + WARNING
        )

    def test_create_slug_with_slugify(self):
        Note.objects.all().delete()
        del self.form_data['slug']
        self.author_client.post(self.notes_add, data=self.form_data)
        self.assertEqual(Note.objects.count(), 1)
        note = Note.objects.get()
        self.assertEqual(note.slug, self.verification_slug)

    def test_author_can_delete_note(self):
        notes_count_start = Note.objects.count()
        self.author_client.delete(self.notes_delete)
        self.assertEqual(notes_count_start - 1, Note.objects.count())

    def test_user_cant_delete_note_of_another_user(self):
        notes_count_start = Note.objects.count()
        response = self.not_author_client.delete(self.notes_delete)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(notes_count_start, Note.objects.count())

    def test_author_can_edit_note(self):
        self.author_client.post(self.notes_edit, data=self.form_data)
        check_note = Note.objects.get(id=self.author_note.id)
        self.assertEqual(check_note.title, self.form_data['title'])
        self.assertEqual(check_note.text, self.form_data['text'])
        self.assertEqual(check_note.author, self.author_note.author)
        self.assertEqual(check_note.slug, self.form_data['slug'])

    def test_user_cant_edit_note_of_another_user(self):
        response = self.not_author_client.post(
            self.notes_edit, data=self.form_data
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        check_note = Note.objects.get(id=self.author_note.id)
        self.assertEqual(check_note.title, self.author_note.title)
        self.assertEqual(check_note.text, self.author_note.text)
        self.assertEqual(check_note.author, self.author_note.author)
        self.assertEqual(check_note.slug, self.author_note.slug)

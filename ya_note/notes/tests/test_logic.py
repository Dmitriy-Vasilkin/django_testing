from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from pytils.translit import slugify

from notes.forms import NoteForm
from notes.models import Note

user = get_user_model()


class BaseCreateAuthorAndLogin(TestCase):
    """Создание авторизованного автора."""
    EDIT_FIELDS = {
        'title': 'Заголовок',
        'text': 'Текст',
        'slug': 'slug'
    }

    @classmethod
    def setUpTestData(cls):
        cls.author = user.objects.create(username='Автор')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.form_data = cls.EDIT_FIELDS


class BaseCreateUser(BaseCreateAuthorAndLogin):
    """Создание пользователя."""
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.user = user.objects.create(username='Пользователь')
        cls.user_client = Client()


class TestNoteCreation(BaseCreateUser):
    """
    Проверка создания записи.

    Методы:
        test_anonymous_user_cant_create_note()
            - анонимный пользователь не может
              создать запись.
        test_user_can_create_note()
            - залогиненный пользователь может
              создать запись.
        checking_add_note()
            - сравнение количества записей
              после попытки создания.
    """

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.add_url = reverse('notes:add')

    def test_anonymous_user_cant_create_note(self):
        self.user_client.post(self.add_url, data=self.form_data)
        self.checking_add_note(0)

    def test_user_can_create_note(self):
        self.author_client.post(self.add_url, data=self.form_data)
        self.checking_add_note(1)

    def checking_add_note(self, expected_values):
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, expected_values)


class TestNoteCreationEqualSlug(BaseCreateAuthorAndLogin):
    """
    Проверка создания записи с идентичным slug.

    Методы:
        test_impossible_equal_slug()
            - пользователь не может создать
              запись с одинаковым slug.
    """

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.form_data['slug'] = 'slug'
        Note.objects.create(
            title='Заголовок',
            text='Просто текст.',
            slug='slug',
            author=cls.author
        )

    def test_impossible_equal_slug(self):
        form = NoteForm(data=self.form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('slug', form.errors)
        self.client.post(reverse('notes:add'), data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)


class TestCreateSlug(BaseCreateAuthorAndLogin):
    """
    Проверка создания записи с незаполненым slug.

    Методы:
        test_create_slug_with_slugify()
            - при незаполненом поле slug
              формируется slug при помощи slugify.
    """

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        del cls.form_data['slug']
        cls.verification_slug = slugify(cls.EDIT_FIELDS['title'])
        cls.add_url = reverse('notes:add')

    def test_create_slug_with_slugify(self):
        self.author_client.post(self.add_url, data=self.form_data)
        note = Note.objects.first()
        self.assertEqual(note.slug, self.verification_slug)


class TestCommentEditDelete(BaseCreateUser):
    """
    Проверка удаления и редактирования записи.

    Методы:
        test_author_can_delete_note()
            - автор может удалить свою запись.
        test_user_cant_delete_note_of_another_user()
            - пользователь не может удалить чужую запись.
        checking_delete_note()
            - проверка количества записей.
        test_author_can_edit_note()
            - автор может редактировать свою запись.
        test_user_cant_edit_note_of_another_user()
            - пользователь не может редактировать
              чужую запись.
        checking_edit_note()
            - проверка изменилась ли запись после редактирования.
    """

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.user_client.force_login(cls.user)
        cls.note = Note.objects.create(
            title='Заголовок_1',
            text='Текст_1',
            slug='slug_1',
            author=cls.author
        )
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))

    def test_author_can_delete_note(self):
        self.author_client.delete(self.delete_url)
        self.checking_delete_note(0)

    def test_user_cant_delete_note_of_another_user(self):
        response = self.user_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.checking_delete_note(1)

    def checking_delete_note(self, expected_values):
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, expected_values)

    def test_author_can_edit_note(self):
        self.author_client.post(self.edit_url, data=self.form_data)
        self.checking_edit_note('')

    def test_user_cant_edit_note_of_another_user(self):
        response = self.user_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.checking_edit_note('_1')

    def checking_edit_note(self, suffix):
        self.note.refresh_from_db()
        for attr, expected_values in self.EDIT_FIELDS.items():
            self.assertEqual(
                getattr(self.note, attr), expected_values + suffix
            )

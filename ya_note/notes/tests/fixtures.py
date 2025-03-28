from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note


user = get_user_model()


class Fixtures(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = user.objects.create(username='Автор')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

        cls.not_author = user.objects.create(username='Не автор')
        cls.not_author_client = Client()
        cls.not_author_client.force_login(cls.not_author)

        cls.author_note = Note.objects.create(
            title='Заголовок автора',
            text='Текст автора',
            slug='slug_author',
            author=cls.author
        )

        cls.not_author_notes = [
            Note(
                title=f'Заголовок {index}',
                text='Просто текст.',
                slug=f'slug_{index}',
                author=cls.not_author
            )
            for index in range(5)
        ]
        Note.objects.bulk_create(cls.not_author_notes)

        cls.slug_author = cls.author_note.slug
        cls.notes_home = reverse('notes:home')
        cls.users_login = reverse('users:login')
        cls.users_logout = reverse('users:logout')
        cls.users_signup = reverse('users:signup')
        cls.notes_list = reverse('notes:list')
        cls.notes_success = reverse('notes:success')
        cls.notes_add = reverse('notes:add')
        cls.notes_detail = reverse('notes:detail', args=(cls.slug_author,))
        cls.notes_edit = reverse('notes:edit', args=(cls.slug_author,))
        cls.notes_delete = reverse('notes:delete', args=(cls.slug_author,))

        cls.redirect_notes_list = f'{cls.users_login}?next={cls.notes_list}'
        cls.redirect_notes_success = (
            f'{cls.users_login}?next={cls.notes_success}'
        )
        cls.redirect_notes_add = f'{cls.users_login}?next={cls.notes_add}'
        cls.redirect_notes_detail = (
            f'{cls.users_login}?next={cls.notes_detail}'
        )
        cls.redirect_notes_edit = f'{cls.users_login}?next={cls.notes_edit}'
        cls.redirect_notes_delete = (
            f'{cls.users_login}?next={cls.notes_delete}'
        )

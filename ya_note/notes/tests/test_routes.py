from http import HTTPStatus

from .fixtures import Fixtures


class TestRoutes(Fixtures):
    """
    Тестирование маршрутов.

    Методы:
        test_routes()
            - тест маршрутов.
        test_redirect()
            - тест редиректов.
    """

    def test_routes(self):
        url_paths_check_status = (
            (self.notes_home, self.client, HTTPStatus.OK),
            (self.users_login, self.client, HTTPStatus.OK),
            (self.users_logout, self.client, HTTPStatus.OK),
            (self.users_signup, self.client, HTTPStatus.OK),
            (self.notes_add, self.author_client, HTTPStatus.OK),
            (self.notes_list, self.author_client, HTTPStatus.OK),
            (self.notes_success, self.author_client, HTTPStatus.OK),
            (self.notes_edit, self.author_client, HTTPStatus.OK),
            (self.notes_delete, self.author_client, HTTPStatus.OK),
            (self.notes_detail, self.author_client, HTTPStatus.OK),
            (self.notes_edit, self.not_author_client, HTTPStatus.NOT_FOUND),
            (self.notes_delete, self.not_author_client, HTTPStatus.NOT_FOUND),
            (self.notes_detail, self.not_author_client, HTTPStatus.NOT_FOUND),
        )
        for (
            reverse_url, parametrized_client, http_status
        ) in url_paths_check_status:
            with self.subTest(
                reverse_url=reverse_url, http_status=http_status
            ):
                response = parametrized_client.get(reverse_url)
                self.assertEqual(response.status_code, http_status)

    def test_redirect(self):
        url_paths_redirect = (
            (self.notes_list, self.redirect_notes_list),
            (self.notes_success, self.redirect_notes_success),
            (self.notes_add, self.redirect_notes_add),
            (self.notes_detail, self.redirect_notes_detail),
            (self.notes_edit, self.redirect_notes_edit),
            (self.notes_delete, self.redirect_notes_delete),
        )
        for reverse_url, redirect_url in url_paths_redirect:
            with self.subTest(
                reverse_url=reverse_url, redirect_url=redirect_url
            ):
                response = self.client.get(reverse_url)
                self.assertRedirects(response, redirect_url)

from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from posts.models import Group, Post

from .test_models import PostModelTest

User = get_user_model()


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test_slug',
            description='Тестовое описание'
        )
        cls.user = User.objects.create_user(username='test_user')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )
        cls.non_author = User.objects.create_user(username='non_author')

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.author_client = Client()
        self.author_client.force_login(self.non_author)

    def test_for_public_pages(self):
        """Доступность страниц для неавторизированных пользователей"""
        templates_url_names = {
            '/': 'posts/index.html',
            '/group/test_slug/': 'posts/group_list.html',
            '/profile/test_user/': 'posts/profile.html',
            f'/posts/{PostModelTest.post.id}/': 'posts/post_detail.html',
        }
        for path, template in templates_url_names.items():
            with self.subTest(path=path):
                self.assertTemplateUsed(
                    self.guest_client.get(path), template)

    def test_pages_only_authorized(self):
        """Страница доступна только для авторизированного пользователя"""
        templates_url_names = {
            '/create/': 'posts/create_post.html',
            f'/posts/{PostModelTest.post.id}/edit/': 'posts/create_post.html',
        }
        for path, template in templates_url_names.items():
            with self.subTest(path=path):
                self.assertTemplateUsed(
                    [self.author_client.get(path),
                     self.authorized_client.get(path), template])

    def test_urls_no_page(self):
        """Проверяем недоступность несуществующей страницы."""
        clients = {
            self.guest_client,
            self.authorized_client,
            self.author_client,
        }
        for client in clients:
            with self.subTest(client=client):
                self.assertEqual(
                    client.get('/unexisting_page/').status_code,
                    HTTPStatus.NOT_FOUND,
                )

    def test_for_public_pages_status(self):
        """Проверяем статус страниц доступных пользователям.
        Главная страница, страница группы, страница автора и страница поста
        """
        templates_url_names = {
            '/': HTTPStatus.OK,
            '/group/test_slug/': HTTPStatus.OK,
            '/profile/test_user/': HTTPStatus.OK,
            f'/posts/{PostModelTest.post.id}/': HTTPStatus.OK,
        }
        for path, template in templates_url_names.items():
            with self.subTest(path=path):
                self.assertEqual(
                    self.authorized_client.get(path).status_code, template,
                    HTTPStatus.OK)

    def test_404_response_code(self):
        """Проверяем возврат страницы 404"""
        response = self.guest_client.get('/SomeOne/', follow=True)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

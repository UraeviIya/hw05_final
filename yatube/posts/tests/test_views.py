import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Comment, Follow, Group, Post

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        cache.clear()
        super().setUpClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test_slug',
            description='Тестовое описание'
        )
        cls.group_2 = Group.objects.create(
            title='Тестовый заголовок_2',
            slug='test_slug_2',
            description='Тестовое описание_2'
        )
        cls.user = User.objects.create_user(username='SomeName')
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )

        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            group=PostViewsTests.group,
            text='Тестовый пост',
            author=User.objects.get(username='SomeName'),
            image=uploaded
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            text='Тестовый комментарий',
            author=cls.user,
        )

    def setUp(self):
        cache.clear()
        self.user = PostViewsTests.user
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.comment = PostViewsTests.comment

    def test_img_on_page(self):
        """Проверяем отоброжение картинки на страницах"""
        urls = (
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            reverse('posts:profile', kwargs={'username': self.user}),
        )
        for path in urls:
            with self.subTest(path=path):
                self.assertEqual(self.authorized_client.get(path).context[
                    'page_obj'][0].image, self.post.image.name)

    def test_cach_in_index_page(self):
        """Проверяем кеширование главной страницы."""
        response = self.authorized_client.get(reverse('posts:index'))
        with_cache = response.content
        Post.objects.create(
            group=PostViewsTests.group,
            text='Новый текст, после кэша',
            author=PostViewsTests.user,
        )
        cache.clear()
        response = self.authorized_client.get(reverse('posts:index'))
        after_clearing_the_cache = response.content
        self.assertNotEqual(with_cache, after_clearing_the_cache)

    def test_views_correct_template(self):
        """Проверяем соответствие view-функций адресам."""
        templates_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': self.group.slug}):
            'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': self.user}):
            'posts/profile.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}):
            'posts/create_post.html',
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}):
            'posts/post_detail.html',
        }
        for path, template in templates_names.items():
            with self.subTest(path=path):
                self.assertTemplateUsed(self.authorized_client.get(
                    path), template)

    def test_index_page_show_correct_context(self):
        """Пост отображается на главной странице"""
        self.assertEqual(self.authorized_client.get(reverse(
            'posts:index')).context['page_obj'][0], self.post)

    def test_group_list_page_correct_context(self):
        """Проверяем отображения поста на странице группы"""
        path = reverse('posts:group_list', kwargs={'slug': self.group.slug})
        self.assertEqual(self.authorized_client.get(path).context[
            'page_obj'][0], self.post)
        self.assertEqual(self.authorized_client.get(path).context[
            'page_obj'][0].group, self.group)
        self.assertEqual(self.authorized_client.get(path).context[
            'page_obj'][0].text, self.post.text)

    def test_profile_page_correct_context(self):
        """Проверяем контекст profile."""
        path = reverse('posts:profile', kwargs={'username': self.user})
        self.assertEqual(self.authorized_client.get(path).context[
            'page_obj'][0], self.post)
        self.assertEqual(self.authorized_client.get(path).context[
            'page_obj'][0].author, self.post.author)

    def test_post_detail_show_correct_context(self):
        """Проверяем отфильтрованный пост по id /post_detail/, с кортинкой"""
        path = reverse('posts:post_detail', kwargs={
                       'post_id': f'{self.post.id}'}
                       )
        self.assertEqual(self.post.id, self.authorized_client.get(
            path).context['post'].id, self.post.image.name)

    def test_create_post_show_correct_context(self):
        """Форма создания поста.
        Форма редактирования поста, отфильтрованного по id
        """
        path_1 = reverse('posts:post_edit', kwargs={
                         'post_id': f'{self.post.id}'}
                         )
        path = reverse('posts:post_create')
        response = self.authorized_client.get(path_1)
        response = self.authorized_client.get(path)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_new_post_exists(self):
        """Проверяем отоброжение поста на страницах"""
        urls = (
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            reverse('posts:profile', kwargs={'username': self.user}),
        )
        for path in urls:
            with self.subTest(path=path):
                self.assertEqual(self.authorized_client.get(path).context[
                    'page_obj'][0].text, self.post.text)

    def test_new_post__in_group(self):
        """Проверяем что пост попал в свою группу."""
        self.assertNotEqual(
            self.authorized_client.get(reverse('posts:index')).context.get(
                'page_obj')[0].group, self.group_2)

    def test_add_comment(self):
        """Проверяем что комментарий создается и
         появляется на странице поста
         """
        form_data = {
            'author': self.user,
            'text': self.comment.text,
            'post_id': self.post.id,
        }
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('posts:post_detail', kwargs={
            'post_id': self.post.id}))
        self.assertTrue(Comment.objects.filter(author=self.user,
                        text=self.comment.text,
                        post_id=self.post.id,).exists())

    def test_follow_index(self):
        """Проверка поста в ленте подписчиков и не подписчиков,
        если user не подписан на автора, посты не появятся в ленте
        """
        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.authorized_client.get(
            reverse('posts:profile_follow', args=[self.user]))
        after_follow = self.authorized_client.get(
            reverse('posts:follow_index'))
        self.assertEqual(response.content, after_follow.content)


class FollowingTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create(
            username='Блогер'
        )
        cls.follower = User.objects.create(
            username='Подписчик'
        )

    def test_login_user_follow(self):
        """Проверяем работу подписки на блогера"""
        self.assertEqual(Follow.objects.count(), 0)
        client_follower = Client()
        client_follower.force_login(self.follower)

        client_follower.get(
            reverse(
                'posts:profile_follow',
                args=(self.author.username,)
            )
        )
        self.assertEqual(Follow.objects.count(), 1)
        follow_obj = Follow.objects.first()
        self.assertEqual(follow_obj.author, self.author)
        self.assertEqual(follow_obj.user, self.follower)
        client_follower.get(reverse('posts:profile_follow',
                                    args=(self.author.username,))
                            )
        self.assertEqual(Follow.objects.count(), 1)
        follows = Follow.objects.filter(author=self.author,
                                        user=self.follower)
        self.assertEqual(len(follows), 1)

    def test_login_user_unfollow(self):
        """Проверяем отписку от блогера"""
        self.assertEqual(Follow.objects.count(), 0)
        Follow.objects.create(author=self.author, user=self.follower)
        self.assertEqual(Follow.objects.count(), 1)
        client_follower = Client()
        client_follower.force_login(self.follower)
        client_follower.get(reverse('posts:profile_unfollow',
                                    args=(self.author.username,))
                            )
        self.assertEqual(Follow.objects.count(), 0)
        follows = Follow.objects.filter(author=self.author, user=self.follower)
        self.assertFalse(follows)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUp(self):
        super().setUpClass()
        self.user = User.objects.create_user(username='SomeName')
        self.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test_slug',
            description='Тестовое описание',
        )
        post = []
        for i in range(20):
            post.append(
                Post(text=f'Тестовый пост {i}',
                     group=self.group, author=self.user)
            )
        Post.objects.bulk_create(post)
        cache.clear()

    def test_first_index_page_pagination(self):
        """На первую страницу выводится 10 постов из 20"""
        self.assertEqual(len(self.client.get(reverse('posts:index')).context[
            'page_obj']), settings.PAGINATOR_LIMIT)

    def test_second_index_page_pagination(self):
        """На вторую страницу выводятся оставшиеся 10 постов"""
        self.assertEqual(len(self.client.get(reverse(
            'posts:index') + '?page=2').context[
                'page_obj']), settings.PAGINATOR_LIMIT)

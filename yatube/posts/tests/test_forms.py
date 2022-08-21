import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Group, Post

User = get_user_model()


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            description='Тестовое описание',
            slug='test_slug'
        )
        cls.author = User.objects.create_user(username='SomeName')
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовый пост',
        )
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostCreateFormTests.author)

    def test_form_create(self):
        """Проверяем создание нового поста авторизированным поьзователем.
        После, автор перенаправляется на страницу поста /profile/
        """
        post_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x01\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'group': self.group.id,
            'text': self.post.text,
            'image': uploaded,
        }
        response = self.authorized_client.post(reverse('posts:post_create'),
                                               data=form_data,
                                               follow=True)
        self.assertRedirects(response, reverse('posts:profile',
                             kwargs={'username': self.author}))
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(Post.objects.filter(
            text=self.post.text,
            group=PostCreateFormTests.group,
            image='posts/small.gif').exists())

    def test_form_edit(self):
        """
        Проверяем возможность редактирование поста через форму на странице
        """
        form_data = {
            'text': self.post.text,
            'group': self.group.id
        }
        group = PostCreateFormTests.group
        test_post = Post.objects.create(
            text=self.post.text,
            author=PostCreateFormTests.author,
            group=group
        )
        test_post_id = test_post.id
        posts_count_before = Post.objects.count()
        path = self.authorized_client.post(
            reverse(
                'posts:post_edit', kwargs={'post_id': self.post.id}
            ),
            data=form_data,
            follow=True
        )
        self.assertRedirects(path, reverse('posts:post_detail', kwargs={
            'post_id': self.post.id}))
        edited_post = Post.objects.get(id=test_post_id)
        self.assertEqual(Post.objects.count(), posts_count_before)
        self.assertEqual(edited_post.text, form_data['text'])
        self.assertEqual(edited_post.group, self.group)
        self.assertEqual(edited_post.author, PostCreateFormTests.author)

from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='SomeName')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        post = PostModelTest.post
        expected_object_name = post.text[:15]
        self.assertEqual(expected_object_name, str(post))
        group = PostModelTest.group
        expected_object_name = group.title
        self.assertEqual(expected_object_name, str(group))

    def test_title_label(self):
        """verbose_name поля title совпадает с ожидаемым."""
        group = PostModelTest.group
        # Получаем из свойста класса Group значение verbose_name для title
        verbose_name = group._meta.get_field('title').verbose_name
        self.assertEqual(verbose_name, 'Название группы')

    def test_help_text_post_group(self):
        """Проверка содержания help_text у модели Post, поля group"""
        post = PostModelTest.post
        help_texts = post._meta.get_field('group').help_text
        self.assertEqual(help_texts, 'В какую группу поместим пост?')

    def test_help_text_post_text(self):
        """Проверка содержания help_text у модели Post, поля text"""
        post = PostModelTest.post
        help_texts = post._meta.get_field('text').help_text
        self.assertEqual(help_texts, 'Это обязательное поле для заполнения')

    def test_verbose_name_post_group(self):
        """Проверка содержания verbose_name у модели Post, поля group"""
        post = PostModelTest.post
        verbose_name = post._meta.get_field('group').verbose_name
        self.assertEqual(verbose_name, 'Группа')

    def test_verbose_name_post_text(self):
        """Проверка содержания verbose_name у модели Post, поля text"""
        post = PostModelTest.post
        verbose_name = post._meta.get_field('text').verbose_name
        self.assertEqual(verbose_name, 'Текст поста')

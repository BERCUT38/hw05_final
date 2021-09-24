from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from ..forms import PostForm
from ..models import Group, Post

User = get_user_model()


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создадим запись в БД для проверки доступности адресов
        cls.user = User.objects.create_user(
            username='author2021'
        )
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        cls.group = Group.objects.create(
            title='название группы',
            slug='slag1',
            description='описание',
        )
        cls.post = Post.objects.create(
            text='1Тестовый текст',
            author=cls.user,
            group=cls.group,
        )
        cls.form = PostForm()

    def test_create_post(self):
        """Тест создания поста"""
        form_data = {
            'text': '2Тестовый текст',
            'group': '1'
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('posts:profile', kwargs={
                             'username': f'{ self.user.username }'}))
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_author_0 = first_object.author
        post_group_0 = first_object.group
        self.assertEqual(post_text_0, '2Тестовый текст')
        self.assertEqual(str(post_author_0), f'{ self.user.username }')
        self.assertEqual(str(post_group_0), f'{ self.group.title }')

    def test_redaction_post(self):
        cache.clear()
        """Тест редактирования поста"""
        form_data = {
            'text': '2Тестовый текст'
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={
                    'post_id': f'{ self.post.pk }'}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': f'{ self.post.pk }'}))
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_author_0 = first_object.author
        self.assertEqual(post_text_0, '2Тестовый текст')
        self.assertEqual(str(post_author_0), f'{ self.user.username }')

from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase

from ..models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создадим запись в БД для проверки доступности адреса task/test-slug/
        cls.user1 = User.objects.create_user(
            username='author'
        )
        cls.user2 = User.objects.create_user(
            username='n_author'
        )
        cls.group = Group.objects.create(
            title='название группы',
            slug='slag1',
            description='описание',
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user1,
            group=cls.group
        )

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем автора
        self.author_client = Client()
        # Авторизуем автора
        self.author_client.force_login(self.user1)
        # Создаем неавтора
        self.n_author_client = Client()
        # Авторизуем неавтора
        self.n_author_client.force_login(self.user2)

    def test_urls_for_guest(self):
        cache.clear()
        # Шаблоны по адресам
        templates_url_names = {
            '/': 'posts/index.html',
            f'/group/{self.group.slug}/': 'posts/group_posts.html',
            f'/profile/{self.user1.username}/': 'posts/profile.html',
            f'/posts/{self.post.pk}/': 'posts/post_detail.html',
        }
        for adress, template in templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.guest_client.get(adress)
                self.assertTemplateUsed(response, template)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_users_authorised_author(self):
        # автор редакт и постит.
        templates_url_names = {
            f'/posts/{self.post.pk}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
        }
        for adress, template in templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.author_client.get(adress)
                self.assertTemplateUsed(response, template)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                response = self.guest_client.get(adress)
                self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_urls_users_authorised_n_author(self):
        # не автор редакт и постит.
        response = self.n_author_client.get('/create/')
        self.assertTemplateUsed(response, 'posts/create_post.html')
        response = self.n_author_client.get(f'/posts/{self.post.pk}/edit/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_urls_users_authorised_n_author(self):
        # гость коментирует
        response = self.n_author_client.get(f'/posts/{self.post.pk}/comment/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_urls_404_custom(self):
        response = self.n_author_client.get('/unexist/')
        self.assertTemplateUsed(response, 'core/404.html')

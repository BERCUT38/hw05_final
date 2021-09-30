from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
import tempfile

from ..forms import PostForm
from ..models import Group, Post

User = get_user_model()

MEDIA_ROOT = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
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
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )

    def test_create_post(self):
        """Тест создания поста"""
        form_data = {
            'text': '2Тестовый текст',
            'group': '1',
            'image': self.uploaded
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_author_0 = first_object.author
        post_group_0 = first_object.group
        post_image_0 = first_object.image
        post = Post.objects.get(pk=2)
        sg = post.image
        self.assertEqual(post_text_0, '2Тестовый текст')
        self.assertEqual(str(post_author_0), f'{ self.user.username }')
        self.assertEqual(str(post_group_0), f'{ self.group.title }')
        self.assertEqual(post_image_0, sg)

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

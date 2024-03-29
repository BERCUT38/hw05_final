import datetime as dt
import tempfile
import shutil

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
import tempfile

from http import HTTPStatus
from ..models import Comment, Follow, Group, Post

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class ViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создадим запись в БД для проверки доступности адресов
        cls.following = User.objects.create(username='following')
        cls.following2 = User.objects.create(username='following2')
        cls.user = User.objects.create_user(
            username='author_main'
        )
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        deltat = dt.timedelta(seconds=1)
        cls.group = Group.objects.create(
            title='название группы',
            slug='slag1',
            description='описание',
        )
        cls.group2 = Group.objects.create(
            title='название группы2',
            slug='slag2',
            description='описание2',
        )
        cls.group3 = Group.objects.create(
            title='название группы3',
            slug='slag3',
            description='описание3',
        )

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

        for x in range(0, 13):
            deltat = dt.timedelta(seconds=x)
            posts = Post.objects.create(
                text=f'{x}text_test',
                author=cls.user,
                group=cls.group,
            )
            posts.pub_date = dt.datetime.utcnow() + deltat
            posts.save()

        deltat = dt.timedelta(seconds=25)
        post2 = Post.objects.create(
            text='Тестовый текст2',
            author=cls.user,
            group=cls.group2,
        )
        post2.pub_date = dt.datetime.utcnow() + deltat
        post2.save()

        deltat = dt.timedelta(seconds=50)
        post3 = Post.objects.create(
            text='Тестовый текст3',
            author=cls.user,
            group=cls.group2,
            image=uploaded,
        )
        post3.pub_date = dt.datetime.utcnow() + deltat
        post3.save()

        Follow.objects.create(user=cls.user, author=cls.following)
        cls.post_for_followers = Post.objects.create(
            author=cls.following, text='Сущность бытия'
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_about_page_uses_correct_template(self):
        cache.clear()
        """Шаблон правильных адресов"""
        slug = {
            'slug': f'{ self.group.slug }'
        }
        uname = {
            'username': f'{self.user.username}'
        }
        post = Post.objects.get(pk=5)
        postpk = post.pk
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list', kwargs=slug
            ): 'posts/group_list.html',
            reverse('posts:profile', kwargs=uname): 'posts/profile.html',
            reverse('posts:post_detail',
                    args=[postpk]): 'posts/post_detail.html',
            reverse('posts:post_edit',
                    args=[postpk]): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html'

        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context_with_image(self):
        cache.clear()
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_author_0 = first_object.author
        post_group_0 = first_object.group
        post_date_0 = first_object.pub_date
        post = Post.objects.get(pk=15)
        posttx = post.text
        postpd = post.pub_date
        sg = post.image
        self.assertEqual(post_text_0, f'{ posttx }')
        self.assertEqual(str(post_author_0), f'{ self.user.username }')
        self.assertEqual(str(post_group_0), f'{ self.group2.title }')
        self.assertEqual(str(post_date_0), f'{ postpd }')
        self.assertEqual(first_object.image, sg)

    def test_index_first_page_contains_10_records(self):
        cache.clear()
        response = self.authorized_client.get(reverse('posts:index'))
        # Проверка: количество постов на первой странице равно 10.
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_index_second_page_contains_6_records(self):
        # Проверка: на второй странице должно быть 4 поста.
        response = self.authorized_client.get(
            reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 6)

    def test_post_group_list_pages_show_correct_context(self):
        """Шаблон post_group_list отфильтрован по группе."""
        response = (self.authorized_client.
                    get(reverse('posts:group_list',
                                kwargs={'slug': f'{ self.group.slug }'})))
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_author_0 = first_object.author
        post_group_0 = first_object.group
        post_date_0 = first_object.pub_date
        post = Post.objects.get(pk=13)
        posttx = post.text
        postpd = post.pub_date
        self.assertEqual(post_text_0, f'{ posttx }')
        self.assertEqual(str(post_author_0), f'{ self.user.username }')
        self.assertEqual(str(post_group_0), f'{ self.group.title }')
        self.assertEqual(str(post_date_0), f'{ postpd }')

    def test_post_group_list_picture(self):
        """Шаблон post_group_list отфильтрован по группе."""
        response = (self.authorized_client.
                    get(reverse('posts:group_list',
                                kwargs={'slug': f'{ self.group2.slug }'})))
        first_object = response.context['page_obj'][0]
        post = Post.objects.get(pk=15)
        sg = post.image
        self.assertEqual(first_object.image, sg)

    def test_post_group_list_first_page_contains_10_records(self):
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={
                    'slug': f'{ self.group.slug }'})
        )
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_post_group_list_second_page_contains_4_records(self):
        response = (
            self.authorized_client.get(
                reverse(
                    'posts:group_list',
                    kwargs={'slug': f'{ self.group.slug }'}
                ) + '?page=2'))
        self.assertEqual(
            len(response.context['page_obj']), 3
        )

    def test_post_profile_list_pages_show_correct_context(self):
        cache.clear()
        """Шаблон post_profile отфильтрован по пользователю."""
        response = (self.authorized_client.
                    get(reverse('posts:profile',
                                kwargs={'username': f'{ self.user.username }'}
                                )))
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_author_0 = first_object.author
        post_group_0 = first_object.group
        post_date_0 = first_object.pub_date
        post = Post.objects.get(pk=1)
        posttx = post.text
        postpd = post.pub_date
        self.assertEqual(post_text_0, f'{ posttx }')
        self.assertEqual(str(post_author_0), f'{ self.user.username }')
        self.assertEqual(str(post_group_0), f'{ self.group.title }')
        self.assertEqual(str(post_date_0), f'{ postpd }')
        self.assertEqual(len(response.context['page_obj']), 10)
        response = self.authorized_client.get(
            reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 6)

    def test_post_profile_list_picture(self):
        """Шаблон post_profile отфильтрован по пользователю."""
        response = (self.authorized_client.
                    get(reverse('posts:profile',
                                kwargs={'username': f'{ self.user.username }'}
                                ) + '?page=2'))
        last_object = response.context['page_obj'][4]
        post = Post.objects.get(pk=15)
        sg = post.image
        self.assertEqual(last_object.image, sg)

    def test_post_profile_list_first_page_contains_10_records(self):
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={
                'username': f'{ self.user.username }'
            }))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_post_profile_list_second_page_contains_6_records(self):
        response = (self.authorized_client.get(
            reverse('posts:profile', kwargs={
                'username': f'{ self.user.username }'
            }) + '?page=2'))
        self.assertEqual(
            len(response.context['page_obj']), 5)

    def test_post_detail_pages_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        post = Post.objects.get(pk=15)
        posttx = post.text
        postpd = post.pub_date
        postpk = post.pk
        sg = post.image
        response = (self.authorized_client.
                    get(reverse('posts:post_detail',
                                kwargs={'post_id': f'{ postpk }'})))
        first_object = response.context['post']
        post_text_0 = first_object.text
        post_author_0 = first_object.author
        post_group_0 = first_object.group
        post_date_0 = first_object.pub_date
        self.assertEqual(post_text_0, f'{ posttx }')
        self.assertEqual(str(post_author_0), f'{ self.user.username }')
        self.assertEqual(str(post_group_0), f'{ self.group2.title }')
        self.assertEqual(str(post_date_0), f'{ postpd }')
        self.assertEqual(first_object.image, sg)

    def test_create_post_list_main(self):
        """ Доп проверки создания поста главная страница."""
        cache.clear()
        post = Post.objects.get(pk=15)
        posttx = post.text
        postpd = post.pub_date
        sg = post.image
        response = (self.authorized_client.
                    get(reverse('posts:index')))
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_author_0 = first_object.author
        post_group_0 = first_object.group
        post_date_0 = first_object.pub_date
        self.assertEqual(post_text_0, f'{ posttx }')
        self.assertEqual(str(post_author_0), f'{ self.user.username }')
        self.assertEqual(str(post_group_0), f'{ self.group2.title }')
        self.assertEqual(str(post_date_0), f'{ postpd }')
        self.assertEqual(first_object.image, sg)

    def test_create_post_list_group_list(self):
        """ Пост попадает на страницу группы."""
        post = Post.objects.get(pk=13)
        posttx = post.text
        postpd = post.pub_date
        response = (self.authorized_client.
                    get(reverse('posts:group_list',
                                kwargs={'slug': f'{ self.group.slug }'})))
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_author_0 = first_object.author
        post_group_0 = first_object.group
        post_date_0 = first_object.pub_date
        self.assertEqual(post_text_0, f'{ posttx }')
        self.assertEqual(str(post_author_0), f'{ self.user.username }')
        self.assertEqual(str(post_group_0), f'{ self.group.title }')
        self.assertEqual(str(post_date_0), f'{ postpd }')

    def test_create_post_list_profile(self):
        """ После создания поста пост попадает на страницу автора."""
        post = Post.objects.get(pk=13)
        posttx = post.text
        postpd = post.pub_date
        response = (self.authorized_client.
                    get(reverse('posts:profile',
                                kwargs={'username': f'{ self.user.username }'}
                                )))
        post = Post.objects.get(pk=1)
        posttx = post.text
        postpd = post.pub_date
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_author_0 = first_object.author
        post_group_0 = first_object.group
        post_date_0 = first_object.pub_date
        post = Post.objects.get(pk=1)
        self.assertEqual(post_text_0, f'{ posttx }')
        self.assertEqual(str(post_author_0), f'{ self.user.username }')
        self.assertEqual(str(post_group_0), f'{ self.group.title }')
        self.assertEqual(str(post_date_0), f'{ postpd }')

    def test_create_post_list_group_foraign(self):
        """ Проверка, что этот пост не попал в группу,
            для которой не был предназначен.
        """
        response = (self.authorized_client.
                    get(reverse('posts:group_list',
                                kwargs={'slug': f'{ self.group.slug }'})))
        count_objects = len(response.context['page_obj'])
        """ Создаем группу и пост внутри теста. """
        group4 = Group.objects.create(
            title='название группы4',
            slug='slag4',
            description='описание4',
        )
        deltat = dt.timedelta(seconds=100)
        post4 = Post.objects.create(
            text='Тестовый текст4',
            author=self.user,
            group=group4,
        )
        post4.pub_date = dt.datetime.utcnow() + deltat
        response = (self.authorized_client.
                    get(reverse('posts:group_list',
                                kwargs={'slug': f'{ self.group.slug }'})))
        """ Статус ОК. """
        self.assertEqual(response.status_code, HTTPStatus.OK)
        count_objects_new = len(response.context['page_obj'])
        self.assertEqual(count_objects, count_objects_new)

    def test_context_index_page_cache(self):
        """ Тест работы кэширования
            Проверяет, что в первые 20 секунд после создания поста
            главная страница не меняется
        """
        index_content = self.authorized_client.get(
            reverse('posts:index')).content
        deltat = dt.timedelta(seconds=60)
        npost = Post.objects.create(
            text='new_text',
            author=self.user,
            group=self.group3,
        )
        npost.pub_date = dt.datetime.utcnow() + deltat
        index_content_cache = self.authorized_client.get(
            reverse('posts:index')).content
        self.assertEqual(index_content, index_content_cache)

    def test_context_index_page_cache_clear(self):
        """ Тест работы кэширования
            Проверяет, что, при очистке кеша
            подгружает новую информацию
        """
        index_content = self.authorized_client.get(
            reverse('posts:index')).content
        deltat = dt.timedelta(seconds=60)
        npost = Post.objects.create(
            text='new_text',
            author=self.user,
            group=self.group3,
        )
        npost.pub_date = dt.datetime.utcnow() + deltat
        npost.save()
        cache.clear()
        index_content_cache_clear = self.authorized_client.get(
            reverse('posts:index')).content
        self.assertNotEqual(index_content, index_content_cache_clear)

    def test_comment_create(self):
        """Появление коммента."""
        post = Post.objects.get(pk=15)
        postpk = post.pk
        comment = Comment.objects.create(
            text='Коммент', author=self.user, post=post)
        commenttxt_start = comment.text
        response = self.authorized_client.get(
            reverse('posts:post_detail', args=[postpk])
        )
        commenttxt = response.context['comments'][0].text
        self.assertEqual(commenttxt, commenttxt_start)

    def test_comment_create_auth(self):
        """Авторизованный комментит."""
        post = Post.objects.get(pk=15)
        postpk = post.pk
        data = {
            'text': 'Коммент'
        }
        commenttxt_start = data['text']
        response = self.authorized_client.post(
            reverse(
                'posts:add_comment',
                args=[postpk]
            ),
            data=data,
            follow=True
        )
        response = self.authorized_client.get(
            reverse('posts:post_detail', args=[postpk])
        )
        comment_auth = response.context['comments'][0].author
        comment_txt = response.context['comments'][0].text
        comment_post = response.context['comments'][0].post
        self.assertEqual(comment_txt, commenttxt_start)
        self.assertEqual(self.user, comment_auth)
        self.assertEqual(post, comment_post)

    def test_new_post_for_followers(self):
        """ Новая запись пользователя появляется в ленте тех, кто на него
            подписан.
        """
        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertIn(
            self.post_for_followers, response.context['page_obj'].object_list
        )

    def test_new_post_for_not_followers(self):
        """ Новая запись пользователя не появляется в ленте тех,
            кто не подписан на него.
        """
        user_t = User.objects.create_user(
            username='user_temp'
        )
        new_client = Client()
        new_client.force_login(user_t)
        response = new_client.get(reverse('posts:follow_index'))
        self.assertNotIn(
            self.post_for_followers, response.context['page_obj'].object_list
        )

    def test_auth_follower_1(self):
        """ Тест подписки """
        count_follow = len(Follow.objects.all())
        self.authorized_client.post(reverse(
            'posts:profile_follow', kwargs={
                'username': f'{ self.following2.username }'
            }
        ))
        response = self.authorized_client.get('/follow/')
        count_follow2 = len(Follow.objects.all())
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertNotEqual(count_follow, count_follow2)
        self.assertTrue(
            Follow.objects.filter(
                user=self.user, author=self.following2).exists(),
            'Не подписывается'
        )

    def test_auth_follower_2(self):
        """ Тест отписки """
        count_follow = len(Follow.objects.all())
        self.authorized_client.post(reverse(
            'posts:profile_unfollow', kwargs={
                'username': f'{ self.following.username }'
            }
        ))
        count_follow2 = len(Follow.objects.all())
        self.assertNotEqual(count_follow, count_follow2)
        self.assertIs(
            Follow.objects.filter(
                user=self.user, author=self.following
            ).exists(),
            False
        )

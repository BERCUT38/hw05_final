from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField(verbose_name="Название", max_length=200)
    slug = models.SlugField(verbose_name="slug", unique=True, max_length=200)
    description = models.TextField(verbose_name="описание", null=True)

    def __str__(self):
        return f'{self.title}'


class Post(models.Model):
    text = models.TextField(
        verbose_name="текст поста", help_text="что на душе"
    )
    pub_date = models.DateTimeField(
        verbose_name="дата публикации", auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name="автор",
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True,
        help_text="давай выкладывай"
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name="группа",
        help_text="к какой группе относится"
    )

    def __str__(self):
        return self.text


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Пост'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name="автор",
    )
    text = models.TextField(verbose_name="комментарий")
    created = models.DateTimeField(
        verbose_name="дата публикации", auto_now_add=True)

    class Meta:
        ordering = ('created',)

    def __str__(self):
        return f'{self.text}'


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name="подписчик",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name="автор",
    )

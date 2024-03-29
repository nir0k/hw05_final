import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.models import Comment, Follow, Group, Post

from ..constants import POSTS_PER_PAGE

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='Ivank')
        cls.group = Group.objects.create(
            title='Test group 01',
            slug='test-group-01',
        )
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)
        self.post = Post.objects.create(
            text='Тестовый пост для тестирования',
            author=self.author,
            group=self.group,
            image=self.uploaded,
        )
        self.comment = Comment.objects.create(
            text='Тестовый комент для тестирования',
            author=self.author,
            post=self.post,
        )

    def tearDown(self):
        cache.clear()

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        cache.clear()
        templates_page_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': self.author.username}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.pk}
            ): 'posts/post_detail.html',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.pk}
            ): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        for reverse_name, template in templates_page_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.guest_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        post_fields = {
            first_object.text: self.post.text,
            first_object.group: self.post.group,
            first_object.author: self.post.author,
            first_object.image: self.post.image,
        }
        for field, expected in post_fields.items():
            with self.subTest(field=field):
                self.assertEqual(field, expected)

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.guest_client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}
            )
        )
        first_object = response.context['page_obj'][0]
        post_fields = {
            first_object.text: self.post.text,
            first_object.author: self.post.author,
            first_object.image: self.post.image,
        }
        for field, expected in post_fields.items():
            with self.subTest(field=field):
                self.assertEqual(field, expected)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.guest_client.get(
            reverse(
                'posts:profile',
                kwargs={'username': self.author.username}
            )
        )
        first_object = response.context['page_obj'][0]
        post_fields = {
            first_object.text: self.post.text,
            first_object.author: self.post.author,
            first_object.image: self.post.image,
        }
        for field, expected in post_fields.items():
            with self.subTest(field=field):
                self.assertEqual(field, expected)

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.guest_client.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.pk}
            )
        )
        post_fields = {
            response.context['post'].text: self.post.text,
            response.context['post'].image: self.post.image,
            response.context["posts_count"]: 1,
            response.context['comments'][0]: self.post.comments.all()[0],
        }
        for field, expected in post_fields.items():
            with self.subTest(field=field):
                self.assertEqual(field, expected)

    def test_post_edit_page_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.pk}
            )
        )
        post_fields = {
            response.context['is_edit']: True,
            response.context['post']: self.post,
            response.context['form']['group'].initial: self.post.group.pk,
            response.context['form']['text'].initial: self.post.text,
            response.context['form']['image'].initial: self.post.image,
        }
        for field, expected in post_fields.items():
            with self.subTest(field=field):
                self.assertEqual(field, expected)

    def test_post_create_page_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_create')
        )
        post_fields = {
            response.context['form']['group'].initial: None,
            response.context['form']['text'].initial: None,
            response.context['form']['image'].initial: None,
        }
        for field, expected in post_fields.items():
            with self.subTest(field=field):
                self.assertEqual(field, expected)

    def test_paginator(self):
        """Тестирование работы пагинатора"""
        group_pagi = Group.objects.create(
            title='Test group 02',
            slug='test-02',
        )
        texts = ['This test text %d' % i for i in range(23)]
        for text in texts:
            Post.objects.create(
                text=text,
                author=self.author,
                group=group_pagi,
            )
        paginator_dict = {
            reverse('posts:index'): POSTS_PER_PAGE,
            reverse('posts:index') + '?page=3': 4,
            reverse(
                'posts:group_list',
                kwargs={'slug': group_pagi.slug}
            ): POSTS_PER_PAGE,
            reverse(
                'posts:group_list',
                kwargs={'slug': group_pagi.slug}
            ) + '?page=3': 3,
            reverse(
                'posts:profile',
                kwargs={'username': self.author.username}
            ): POSTS_PER_PAGE,
            reverse(
                'posts:profile',
                kwargs={'username': self.author.username}
            ) + '?page=3': 4,
        }
        for reverse_value, expected in paginator_dict.items():
            with self.subTest(reverse_value=reverse_value):
                response = self.client.get(reverse_value)
                self.assertEqual(len(response.context['page_obj']), expected)

    def test_follow_author(self):
        """Тестирование возможности подписки и одписки от автора"""
        author1 = User.objects.create_user(username='author1')
        user = User.objects.create_user(username='user')
        authorized_client = Client()
        authorized_client.force_login(user)
        follow_count = Follow.objects.filter(
            user=user,
            author=author1
        ).count()
        authorized_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': author1.username}
            )
        )
        self.assertEqual(
            Follow.objects.filter(
                user=user,
                author=author1
            ).count(),
            follow_count + 1
        )
        authorized_client.get(
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': author1.username}
            )
        )
        self.assertEqual(
            Follow.objects.filter(
                user=user,
                author=author1
            ).count(),
            follow_count
        )

    def test_view_following_posts(self):
        """Тестирование отображения постов на авторов
        на которых подписан пользователь"""
        author1 = User.objects.create_user(username='author1')
        author2 = User.objects.create_user(username='author2')
        user1 = User.objects.create_user(username='user1')
        user2 = User.objects.create_user(username='user2')
        authorized_client1 = Client()
        authorized_client2 = Client()
        authorized_client1.force_login(user1)
        authorized_client2.force_login(user2)
        Post.objects.create(text='text', author=author1,)
        Post.objects.create(text='text', author=author2,)
        authorized_client1.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': author2.username}
            )
        )
        response1 = authorized_client1.get(reverse('posts:follow_index'))
        self.assertEqual(len(response1.context['page_obj']), 1)
        first_object = response1.context['page_obj'][0]
        self.assertEqual(first_object.author, author2)
        response2 = authorized_client2.get(reverse('posts:follow_index'))
        self.assertEqual(len(response2.context['page_obj']), 0)

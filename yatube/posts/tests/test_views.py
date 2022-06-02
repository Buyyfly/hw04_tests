from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from ..models import Group, Post

User = get_user_model()


class TaskURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='HasNoName')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Описание',
        )
        for i in range(settings.POSTS_PAGE + 1):
            cls.post = Post.objects.create(
                author=cls.user,
                text='Тестовый пост',
                group=cls.group
            )
        cls.templates_paginator_test = {
            'posts/index.html': reverse('posts:post_list'),
            'posts/group_list.html': reverse(
                'posts:group_list',
                kwargs={'slug': f'{cls.group.slug}'}
            ),
            'posts/profile.html': reverse(
                'posts:profile',
                kwargs={'username': f'{cls.user.username}'}
            ),
        }

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            'posts/index.html': reverse('posts:post_list'),
            'posts/group_list.html': reverse(
                'posts:group_list',
                kwargs={'slug': f'{self.group.slug}'}
            ),
            'posts/profile.html': reverse(
                'posts:profile',
                kwargs={'username': f'{self.user.username}'}
            ),
            'posts/post_detail.html': reverse(
                'posts:post_detail',
                kwargs={'post_id': f'{self.post.id}'}
            ),
            'posts/create_post.html': reverse('posts:post_create'),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

        response = self.authorized_client.get(
            reverse('posts:post_edit',
                    kwargs={'post_id': f'{self.post.id}'})
        )
        self.assertTemplateUsed(response, 'posts/create_post.html')

    def test_paginator(self):
        for template, reverse_name in self.templates_paginator_test.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertEqual(len(response.context['page_obj']),
                                 settings.POSTS_PAGE)
                response = self.authorized_client.get(reverse_name + '?page=2')
                self.assertEqual(len(response.context['page_obj']), 1)

    def test_templates_pages_names_paginator_context(self):
        for template, reverse_name in self.templates_paginator_test.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertIn('page_obj', response.context)
                first_object = response.context['page_obj'][0]
                TaskURLTests.cs(self,
                                text=first_object.text,
                                author=first_object.author,
                                group=first_object.group)

    def test_post_detail_context(self):
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': f'{self.post.id}'})
        )
        self.assertIn('post', response.context)
        first_object = response.context['post']
        self.assertNotEqual(first_object.group, 'NoGroup')
        TaskURLTests.cs(self,
                        text=first_object.text,
                        author=first_object.author,
                        group=first_object.group)

    def test_create_edit_post_context(self):
        templates_create_edit = {
            1: reverse('posts:post_create'),
            2: reverse('posts:post_edit',
                       kwargs={'post_id': f'{self.post.id}'})
        }
        for template, reverse_name in templates_create_edit.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)

                form_fields = {
                    'text': forms.fields.CharField,
                    'group': forms.fields.ChoiceField,
                }
                for value, expected in form_fields.items():
                    with self.subTest(value=value):
                        form_field = response.context.get(
                            'form'
                        ).fields.get(value)
                        self.assertIsInstance(form_field, expected)

    def cs(self, text, author, group):
        self.assertEqual(text, 'Тестовый пост')
        self.assertEqual(group, self.group)
        self.assertEqual(author, self.user)
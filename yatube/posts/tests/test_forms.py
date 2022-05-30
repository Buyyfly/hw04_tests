from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

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
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            id='111',
            group=cls.group
        )

    def test_create_post(self):
        post_count = Post.objects.count()
        form_data = {
            'text': 'text',
            'group': self.group.pk,
        }
        response = self.authorized_client.post(reverse('posts:post_create'),
                                               data=form_data, follow=True)
        self.assertRedirects(response,
                             reverse(
                                 'posts:profile',
                                 kwargs={'username':  self.user})
                             )
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(
            Post.objects.filter(
                group=self.group,
                author=self.user,
                text='text'
            ).exists()
        )

    def test_edit_post(self):
        form_data = {
            'text': 'text1',
            'group': self.group.pk,
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit',
                    kwargs={'post_id': '111'}),
            data=form_data, follow=True)
        self.assertRedirects(response,
                             reverse('posts:post_detail',
                                     kwargs={'post_id': '111'})
                             )
        self.assertTrue(
            Post.objects.filter(
                group=self.group,
                author=self.user,
                text='text1'
            ).exists()
        )

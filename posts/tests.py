from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User


class ProfileTest(TestCase):

    def setUp(self):
        self.client_logged = Client()
        self.client_logged_1 = Client()
        self.client_logged_2 = Client()
        self.client_unlogged = Client()
        cache.clear()
        self.user = User.objects.create_user(username='new_user', email='ya@ya.ru', password='12345')
        self.user_1 = User.objects.create_user(username='TestUser_1', password='test1')
        self.user_2 = User.objects.create_user(username='TestUser_2', password='test2')
        self.client_logged.force_login(self.user)
        self.client_logged_1.force_login(self.user_1)
        self.client_logged_2.force_login(self.user_2)
        self.group = Group.objects.create(title='Test_group', slug='Test_group')
        self.post = Post.objects.create(text='New_test_post', author=self.user, group=self.group)

    def test_new_user_profile_page(self):
        response = self.client_logged.get(reverse('profile', args=[self.user.username]))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['author'], User)
        self.assertEqual(response.context['author'], self.user)

    def test_new_post_create(self):
        response = self.client_logged.get(reverse('new_post'))
        self.assertEqual(response.status_code, 200)
        self.client_logged.post(reverse('new_post'), {'group': self.group.id, 'text': 'test_text'})
        response = self.client_logged.get(reverse('index'))
        self.assertEqual('test_text', response.context['page'][0].text)

    def test_new_post_views(self):
        test_urls = [
            reverse('index'),
            reverse('profile', args=(self.user.username,),),
            reverse('group', args=(self.group.slug,),),
        ]
        for url in test_urls:
            response = self.client_logged.get(url)
            self.assertIn(self.post, response.context['page'].object_list)
        response = self.client_logged.get(reverse('post', args=(self.user.username, self.post.id)))
        self.assertEqual(response.status_code, 200)

    def test_post_edit(self):
        response = self.client_logged.get(
            reverse('post_edit', kwargs={'username': self.user.username, 'post_id': self.post.id, }))
        self.assertEqual(response.status_code, 200)
        self.client_logged.post(
            reverse('post_edit', kwargs={'username': self.user.username, 'post_id': self.post.id, }),
            {'text': self.post.id, 'group': self.group.id, }, follow=True)
        response = self.client_logged.get(reverse('post', args=(self.user.username, self.post.id)))
        self.assertEqual(f'{self.post.id}', response.context['post'].text)
        response = self.client_logged.get(reverse('index'))
        page = response.context['page']
        for test_posts in page:
            if test_posts.id == self.post.id:
                test_posts_text = test_posts.text
                self.assertEqual(f'{self.post.id}', test_posts_text)
                break
        response = self.client_logged.get(reverse('group', args=[self.group.slug]))
        page = response.context['page']
        for test_posts in page:
            if test_posts.id == self.post.id:
                test_posts_text = test_posts.text
        self.assertEqual(f'{self.post.id}', test_posts_text)

    def test_unauthorized_user_create_post(self):
        count_posts = Post.objects.all().count()
        response = self.client_unlogged.post(
            reverse('new_post'), {'group': 'New_test_group', 'text': 'test_text'}
            )
        count_posts_after_post = Post.objects.all().count()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(count_posts, count_posts_after_post)

    def test_unauthorized_user_edit_post(self):
        response = self.client_unlogged.get(
            reverse('post_edit', kwargs={'username': self.user.username, 'post_id': self.post.id, }))
        self.assertEqual(response.status_code, 302)

    def test_404(self):
        response = self.client_unlogged.get('getmethe404pageplease')
        self.assertEqual(response.status_code, 404)

    def test_new_post_with_img(self):
        with open('media/posts/horosh.png', 'rb') as img:
            response = self.client_logged.post(
                reverse('new_post'),
                {'author': self.user, 'text': 'post with image',
                 'image': img, 'group': self.group.id, }, follow=True
                )
        response = self.client_logged.get(reverse('index'))
        self.assertEqual('post with image', response.context['page'][0].text)
        self.assertIn('<img'.encode(), response.content)
        test_urls = [
            reverse('index'),
            reverse('profile', args=(self.user.username,),),
            reverse('group', args=(self.group.slug,),),
        ]
        for url in test_urls:
            response = self.client_logged.get(url)
            self.assertIn('<img'.encode(), response.content)

    def test_active_user_following_unfollowing(self):
        response = self.client_logged.get(reverse('profile_follow', args=(self.user_1.username,)), follow=True)
        self.assertEqual(response.context['fwers_count'], 1)
        response = self.client_logged.get(reverse('profile', args=(self.user.username,)))
        self.assertEqual(response.context['fwing_count'], 1)
        response = self.client_logged.get(reverse('profile_unfollow', args=(self.user_1.username,)), follow=True)
        self.assertEqual(response.context['fwers_count'], 0)
        response = self.client_logged.get(reverse('profile', args=(self.user.username,)))
        self.assertEqual(response.context['fwing_count'], 0)

    def test_new_post_in_subscription(self):
        self.client_logged.get(reverse('profile_follow', args=(self.user_2.username,)), follow=True)
        self.client_logged_2.post(reverse('new_post'), {'group': self.group.id, 'text': 'subscription_test_123!'})
        response = self.client_logged.get(reverse('follow_index'))
        self.assertIn('subscription_test_123!\n', response.content.decode())
        response = self.client_logged_1.get(reverse('follow_index'))
        self.assertNotEqual('subscription_test_123!\n', response.content.decode())

    def test_unauth_user_no_comment(self):
        Post.objects.create(
            text='Тестовый пост для проверки комментировать только авторизованному юзеру', author=self.user_1,
        )
        response = self.client_unlogged.get(
            reverse('post', kwargs={'username': self.user_1.username, 'post_id': self.post.id, }),
            follow=True
            )
        self.assertNotIn('Добавить комментарий:', response.content.decode())
        response = self.client_logged.post(
            reverse('add_comment', kwargs={'username': self.user_1.username, 'post_id': self.post.id, }),
            data={'text': 'Новый коммент123!@#!'}, follow=True
            )
        self.assertIn('Новый коммент123!@#!', response.content.decode())

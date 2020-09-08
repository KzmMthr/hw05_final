import datetime as dt
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files import File
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User


class ProfileTest(TestCase):

    def setUp(self):
        self.client_logged = Client()
        self.client_unlogged = Client()
        cache.clear()
        self.user = User.objects.create_user(username='new_user', email='ya@ya.ru', password='12345')
        self.client_logged.force_login(self.user)
        self.group = Group.objects.create(title='Test_group', slug='Test_group')
        self.post = Post.objects.create(text='New_test_post', author=self.user, group=self.group)

    def test_new_user_profile_page(self):
        response = self.client_logged.get(reverse('profile', args=[self.user.username]))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['author'], User)
        self.assertEqual(response.context['author'], self.user)

    def test_new_post(self):
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
        response = self.client_unlogged.post(reverse('new_post'), {'group': 'New_test_group', 'text': 'test_text'})
        count_posts_after_post = Post.objects.all().count()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(count_posts, count_posts_after_post)
        
    def test_unauthorized_user_edit_post(self): 
        response = self.client_unlogged.get(
            reverse('post_edit', kwargs={'username': self.user.username, 'post_id': self.post.id, }))
        self.assertEqual(response.status_code, 302)

    def test_404(self):
        response = self.client_unlogged.get('4040404040404040404')
        self.assertEqual(response.status_code, 404)
        
    def test_new_post_with_img(self):
        with open('media/posts/horosh.png','rb') as img:
            response = self.client_logged.post(
                reverse('new_post'), 
                {'author': self.user, 'text': 'post with image', 'image': img, 'group': self.group.id, }, follow=True)
        #проверка что пост создался и в посте есть изображение
        response = self.client_logged.get(reverse('index'))
        self.assertEqual('post with image', response.context['page'][0].text)
        self.assertIn('<img'.encode(), response.content)
        #проверка что тег <IMG> есть на главной, в профиле и группе
        test_urls = [
            reverse('index'),
            reverse('profile', args=(self.user.username,),),
            reverse('group', args=(self.group.slug,),),
        ]
        for url in test_urls:
            response = self.client_logged.get(url)
            self.assertIn('<img'.encode(), response.content)
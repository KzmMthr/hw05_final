from django.contrib.auth import get_user_model
from django.db import models


User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField('URL', max_length=50, unique=True)
    description = models.TextField()

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField()
    pub_date = models.DateTimeField('date published', auto_now_add=True,)
    author = models.ForeignKey(User, on_delete=models.CASCADE,)
    group = models.ForeignKey(
        Group, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='Group',
        related_name='posts',
    )
    image = models.ImageField(upload_to='posts/', blank=True, null=True) 


    class Meta:
        ordering = ['-pub_date']

    def __str__(self):
        return self.text[:100]


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, blank=False, verbose_name='Post', related_name='comments',)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(max_length=2000)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text[:100]


class Follow(models.Model):
    user = models.ForeignKey(User, verbose_name='User', related_name='follower', on_delete=models.CASCADE)
    author = models.ForeignKey(User, verbose_name='Author', related_name='following', on_delete=models.CASCADE)
    

from django import forms
from django.forms import ModelForm, Textarea

from .models import Post, Comment


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ['group', 'text', 'image', ]
        labels = {'group': 'Группа', 'text': 'Текст поста', 'image': 'Загрузка изображения' }
        help_texts = {'group': "Добавить пост в группу", 'text': 'Напишите текст нового поста', 'image': 'Изображение не более 5Мб'}
        

class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ['text',]
        labels = {'text': 'Текст комментария',}
        help_texts = {'text': 'Напишите текст комментария',}
        widgets = {
            'text': Textarea(attrs={'cols': 60, 'rows': 8}),
        }
        
        

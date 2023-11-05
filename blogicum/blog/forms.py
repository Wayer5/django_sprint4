from .models import Comment, Post
from django import forms
from django.utils import timezone


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'text', 'pub_date', 'location', 'category', 'is_published', 'image']
        widgets = {
            'pub_date': forms.TextInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        self.fields['pub_date'].input_formats = ['%Y-%m-%dT%H:%M:%S']

    def clean_pub_date(self):
        pub_date = self.cleaned_data['pub_date']
        if pub_date < timezone.now():
            raise forms.ValidationError('Дата и время публикации должны быть в будущем.')
        return pub_date

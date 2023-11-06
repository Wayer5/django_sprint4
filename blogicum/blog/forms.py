from django import forms

from .models import Comment, Post, User


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        widgets = {
            'created_at': forms.DateInput(attrs={'type': 'date'}),
            'text': forms.Textarea(attrs={'cols': '22', 'rows': '5'}),
        }


class PostCreateForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'text', 'location', 'category', 'image', 'pub_date')
        widgets = {
            'pub_date': forms.DateInput(attrs={'type': 'date'}),
            'text': forms.Textarea(attrs={'cols': '22', 'rows': '5'}),
        }


class UserCreateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')

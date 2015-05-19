from django import forms

from .models import User, PostWithPicture


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        exclude = ["date_joined"]


class PostWithPictureForm(forms.ModelForm):
    class Meta:
        model = PostWithPicture
        fields = "__all__"

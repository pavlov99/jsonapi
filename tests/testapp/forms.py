from django import forms

from .models import PostWithPicture


class PostWithPictureForm(forms.ModelForm):
    class Meta:
        model = PostWithPicture
        fields = "__all__"

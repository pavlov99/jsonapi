from .settings import settings
from django.db import models


class Author(models.Model):
    pass


class Blog(models.Model):
    pass


class Post(models.Model):
    title = models.CharField(max_length=100)
    author = models.ForeignKey(Author)
    blog = models.ForeignKey(Blog)


class Comment(models.Model):
    post = models.ForeignKey(Post)

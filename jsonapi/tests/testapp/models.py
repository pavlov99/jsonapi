""" Models definition.

Model relationship:

      Author    Blog
       ||        |
       ||        @
       ||-----@ Post ----> PostWithPicture
       |  ______/
       |  |
       @  @
       Comment

"""


from django.db import models


class Author(models.Model):
    pass


class Blog(models.Model):
    pass


class Post(models.Model):
    title = models.CharField(max_length=100)
    author = models.ForeignKey(Author, related_name="comments")
    blog = models.ForeignKey(Blog)


class PostWithPicture(Post):
    picture_url = models.URLField()


class Comment(models.Model):
    post = models.ForeignKey(Post, related_name='comments')

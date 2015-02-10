""" Models definition.

Model relationship:

      Author  auth.User
       ||        |
       ||        @
       ||-----@ Post ----> PostWithPicture
       |  ______/
       |  |
       @  @
       Comment

Also Setup classes with different relationship types for tests.

B is inherited from A
All of the relationship for A class are defined in A
All of the relationship for B class are defined in related classes

There is no OneToMany relationship in Django, so there are no AMany
and BOne classes.

       AAbstractOne      AOne  BManyToMany -> BManyToManyChild
            |              |        @
            |              |        |
            @              @        @
 User--@AAbstract => AA -> A -----> B ------- BProxy
            @              @        |
            |              |        |
            @              @        @
  AAbstractManyToMany AManyToMany BMany

"""
from django.db import models
from django.contrib.auth.models import User


class Author(models.Model):
    name = models.CharField(max_length=100)


class Post(models.Model):
    title = models.CharField(max_length=100)
    author = models.ForeignKey(Author)
    user = models.ForeignKey(User, null=True, blank=True)

    @property
    def title_uppercased(self):
        return self.title.upper()


class PostWithPicture(Post):
    picture_url = models.URLField()


class Comment(models.Model):
    post = models.ForeignKey(Post, related_name='comments')
    author = models.ForeignKey(Author)


class TestSerializerAllFields(models.Model):
    big_integer = models.BigIntegerField()
    # binary = models.BinaryField()
    boolean = models.BooleanField(default=False)
    char = models.CharField(max_length=100)
    comma_separated_integer = models.CommaSeparatedIntegerField(max_length=5)
    date = models.DateField()
    datetime = models.DateTimeField()
    decimal = models.DecimalField(max_digits=2, decimal_places=1)
    email = models.EmailField()
    authorfile = models.FileField(upload_to='.')
    filepath = models.FilePathField()
    floatnum = models.FloatField()
    # image = models.ImageField()  # Avoid Pillow import
    integer = models.IntegerField()
    ip = models.IPAddressField()
    generic_ip = models.GenericIPAddressField(protocol='ipv6')
    nullboolean = models.NullBooleanField()
    positive_integer = models.PositiveIntegerField()
    positive_small_integer = models.PositiveSmallIntegerField()
    slug = models.SlugField()
    small_integer = models.SmallIntegerField()
    text = models.TextField()
    time = models.TimeField()
    url = models.URLField()


class AAbstractOne(models.Model):
    field = models.IntegerField()


class AAbstractManyToMany(models.Model):
    field = models.IntegerField()


class AAbstract(models.Model):
    class Meta:
        abstract = True

    field_abstract = models.IntegerField()
    user = models.ForeignKey(User)
    a_abstract_one = models.ForeignKey(AAbstractOne)
    a_abstract_many_to_manys = models.ManyToManyField(
        AAbstractManyToMany,
        related_name="%(app_label)s_%(class)s_related"
    )


class AA(AAbstract):
    pass


class AOne(models.Model):
    field = models.IntegerField()


class AManyToMany(models.Model):
    field = models.IntegerField()


class A(AA):
    field_a = models.IntegerField()
    a_one = models.ForeignKey(AOne)
    a_many_to_manys = models.ManyToManyField(AManyToMany)


class B(A):
    field_b = models.IntegerField()


class BMany(models.Model):
    field = models.IntegerField()
    b = models.ForeignKey(B, related_name="bmanys")


class BManyToMany(models.Model):
    field = models.IntegerField()
    bs = models.ManyToManyField(B, related_name="bmanytomanys")


class BManyToManyChild(BManyToMany):
    pass


class BProxy(B):
    class Meta:
        proxy = True

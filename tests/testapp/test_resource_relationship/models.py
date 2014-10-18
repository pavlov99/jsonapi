""" Setup classes with different relationship types.

B is inherited from A
All of the relationship for A class are defined in A
All of the relationship for B class are defined in related classes

There is no OneToMany relationship in Django, so there are no AMany
and BOne classes.

    AAbstractOne      AOne  BManyToMany
            |              |        @
            |              |        |
            @              @        @
        AAbstract => AA -> A -----> B ------ BProxy
            @              @        |
            |              |        |
            @              @        @
AAbstractManyToMany AManyToMany BMany

"""
from django.db import models


class AAbstractOne(models.Model):
    field = models.IntegerField()


class AAbstractManyToMany(models.Model):
    field = models.IntegerField()


class AAbstract(models.Model):
    class Meta:
        abstract = True

    field_abstract = models.IntegerField()
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


class BProxy(B):
    class Meta:
        proxy = True

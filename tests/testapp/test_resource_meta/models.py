from django.db import models
from django.contrib.auth.models import AbstractBaseUser


class CustomUser(AbstractBaseUser):
    pass


class A(models.Model):
    pass


class AChild(A):
    pass

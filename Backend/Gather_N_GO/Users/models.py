

# Create your models here.

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    # add additional fields in here
    gender = models.CharField(max_length=10)
    dob = models.DateField(null=True,blank=True)

    def __str__(self):
        return self.username


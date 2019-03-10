from django.db import models
from django import forms
# # Create your models here.


class User(models.Model):
    username = models.CharField(max_length=30)
    email = models.EmailField()
    password = models.CharField(max_length=30)

    def __str__(self):
        return self.username

class UserProfile(models.Model):
    phone=models.CharField(max_length=13)
    sex = models.CharField(max_length=10)
    favourite_colors = models.CharField(max_length=100)
    dob = models.DateField()

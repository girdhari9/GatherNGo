
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import get_user_model


User = get_user_model()

class CustomUserCreationForm(UserCreationForm):

    class Meta(UserCreationForm):
        model = User
        fields = ('username', 'email', 'gender', 'dob')

class CustomUserChangeForm(UserChangeForm):

    class Meta(UserChangeForm):
        model = User
        fields = ('username', 'email', 'gender', 'dob')
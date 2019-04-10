from django.shortcuts import render
from .forms import CustomUserCreationForm

from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views import generic



# Create your views here.

def home(request):
    return render(request, 'home.html')





class SignUp(generic.CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'signup.html'
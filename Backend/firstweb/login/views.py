from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from .forms import UserForm, UserProfileForm, Login
from .models import User
def signup(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        # profile_form=UserProfileForm(request.post)
        if user_form.is_valid():
            user= user_form.save(commit=False)
            # user.password(user.password)
            user.save()
            # profile=profile_form.save(commit=False)
            # profile.user=user
            # profile.save()
            return redirect('/music')
        else:
            print(user_form.errors)


    else:
        user_form = UserForm()
        profile_form=UserProfileForm()
    return render(request, 'login/signup.html', {'form': user_form})

def login(request):
    if request.method == 'POST':
        login_form = Login(request.POST)
        if login_form.is_valid():
            data=request.POST.copy()
            u_name = data.get('username')
            password = data.get('password')
            user = User.objects.get(username=u_name)
            if user.password == password:
                print("success")
            else:
                print("failure")

    else:
        login_form=Login()
    return render(request, 'login/login.html', {'form': login_form})
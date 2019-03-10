from django.contrib import admin
# from .models import login_details
# Register your models here.

from .models import User
admin.site.register(User)

from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from . import models


# Register your models here.
admin.site.register(models.User, auth_admin.UserAdmin)

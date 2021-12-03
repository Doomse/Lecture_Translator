from django.contrib import admin
from django.contrib import auth
from django.contrib.auth import admin as auth_admin
from . import models


class CodeAdmin(admin.ModelAdmin):

    list_display = ['timeout']

    def add_view(self, *args, **kwargs):
        self.fields = ['code', 'timeout']
        return super().add_view(*args, **kwargs)

    def change_view(self, *args, **kwargs):
        self.fields = ['timeout']
        return super().change_view(*args, **kwargs)


# Register your models here.
admin.site.register(models.User, auth_admin.UserAdmin)
admin.site.register(models.Code, CodeAdmin)
from django import forms
from django.contrib.auth import forms as auth_forms
from django.forms import fields
from . import models

class UserRegisterForm(auth_forms.UserCreationForm):

    class Meta(auth_forms.UserCreationForm.Meta):
        model = models.User
from django import forms
from django.utils import safestring
from django.templatetags import static
from datetime import datetime
from . import models
from django.contrib.auth.forms import UserCreationForm, UsernameField


class VerificationForm(forms.Form):

    verification = forms.CharField()

    def clean_verification(self):
        verify = self.cleaned_data['verification']
        for code in models.Code.objects.filter(timeout__gte=datetime.now()):
            if code.check_code(verify):
                return verify
        raise forms.ValidationError('Invalid verification code')


class UserRegisterForm(UserCreationForm):

    agreement = forms.BooleanField(help_text=safestring.mark_safe(f'I accept the this <a href="{static.static("users/agreement.pdf")}" target="_blank">agreement</a>') )

    class Meta:
        model = models.User
        fields = ("username", )
        field_classes = {'username': UsernameField}
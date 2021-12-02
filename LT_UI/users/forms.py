from django import forms
from datetime import datetime
from . import models


class VerificationForm(forms.Form):

    verification = forms.CharField()

    def clean_verification(self):
        verify = self.cleaned_data['verification']
        for code in models.Code.objects.filter(timeout__gte=datetime.now()):
            if code.check_code(verify):
                return verify
        raise forms.ValidationError('Invalid verification code')
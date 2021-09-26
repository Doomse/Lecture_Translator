from django import forms
from django.forms import widgets
from . import models, utils


class TaskForm(forms.ModelForm):
    
    class Meta:
        model = models.Task
        fields = ("title", "source", "language", "translations")
        widgets = {
            'translations': widgets.SelectMultiple(choices=utils.LANGUAGE_CHOICES)
        }

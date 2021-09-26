from django import forms
from . import models, utils


class TaskForm(forms.ModelForm):
    
    translations = forms.MultipleChoiceField(choices=utils.LANGUAGE_CHOICES)

    class Meta:
        model = models.Task
        fields = ("title", "source", "language", "translations")

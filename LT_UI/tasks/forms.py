from django import forms
from . import models, utils


class TaskForm(forms.ModelForm):
    
    translations = forms.MultipleChoiceField(choices=utils.LANGUAGE_CHOICES, widget=forms.widgets.CheckboxSelectMultiple)

    class Meta:
        model = models.Task
        fields = ("title", "source", "language", "translations")
        widgets = {
            'language': forms.widgets.RadioSelect
        }

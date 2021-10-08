from django import forms
from . import models, utils


class TaskForm(forms.ModelForm):
    
    #translations = forms.MultipleChoiceField(choices=utils.LANGUAGE_CHOICES, widget=forms.widgets.CheckboxSelectMultiple)

    class Meta:
        model = models.Task
        fields = ("title", "source", "language", )
        widgets = {
            'language': forms.widgets.RadioSelect
        }


class TaskTranslationForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance is not None:
            print(self.instance)
            self.fields['translations'] = forms.MultipleChoiceField(choices=self.instance.get_translations(), widget=forms.widgets.CheckboxSelectMultiple, required=False)

    class Meta:
        model = models.Task
        fields = ("translations", )
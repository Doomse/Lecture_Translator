from pathlib import Path
from django import forms
from django.core.files import uploadedfile
from django.core.files.base import ContentFile
from . import models
import zipfile


class TaskFilesForm(forms.ModelForm):

    source = forms.FileField(widget=forms.FileInput(attrs={'multiple': True, 'accept': 'audio/*,video/*'}))
    
    def save(self, commit=True):
        # TODO check for duplicate file names
        print(self.cleaned_data)
        obj = super().save(commit)
        for file in self.files.getlist('source'):
            print(type(file))
            st = models.SubTask(title=Path(file.name).stem, task=obj)
            st.source.save(file.name, ContentFile(file.read()))

        return obj

    class Meta:
        model = models.Task
        fields = ("title", "source", "language")
        widgets = {
            'language': forms.RadioSelect,
        }


class TaskTranslationForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance is not None:
            self.fields['translations'] = forms.MultipleChoiceField(choices=self.instance.get_translations(), widget=forms.widgets.CheckboxSelectMultiple, required=False)

    class Meta:
        model = models.Task
        fields = ("translations", )


class TaskReturnForm(forms.Form):

    cfile = forms.FileField(widget=forms.FileInput(attrs={'accept': 'text/vtt'}))
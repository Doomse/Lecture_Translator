from django import forms
from django.core.files import uploadedfile
from . import models
import zipfile


class TaskZipForm(forms.ModelForm):
    
    #translations = forms.MultipleChoiceField(choices=utils.LANGUAGE_CHOICES, widget=forms.widgets.CheckboxSelectMultiple)

    class Meta:
        model = models.Task
        fields = ("title", "source", "language", )
        widgets = {
            'language': forms.RadioSelect,
            'source': forms.FileInput(attrs={'accept': 'application/zip'}),
        }


class TaskFilesForm(TaskZipForm):

    #Rearrange the file list into a single zip archive
    def clean_source(self):
        data = uploadedfile.SimpleUploadedFile('name', b'')
        with zipfile.ZipFile(data, 'w') as zf:
            for file in self.files.getlist('source'):
                zf.writestr(file.name, file.read())
        return data

    class Meta(TaskZipForm.Meta):
        widgets = TaskZipForm.Meta.widgets
        widgets['source'] = forms.FileInput(attrs={'multiple': True, 'accept': 'audio/*,video/*'})


class TaskTranslationForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance is not None:
            self.fields['translations'] = forms.MultipleChoiceField(choices=self.instance.get_translations(), widget=forms.widgets.CheckboxSelectMultiple, required=False)

    class Meta:
        model = models.Task
        fields = ("translations", )
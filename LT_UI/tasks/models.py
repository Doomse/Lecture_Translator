from django.core import exceptions
from django.db import models
from django.contrib import auth
from django.core.files import base
from . import utils, workers
import threading


def source_path(instance, filename):
    return instance.owner.username + f'/source_{instance.title}.zip'

def result_path(instance, filename):
    return instance.owner.username + f'/result_{instance.title}.zip'


class ListField(models.CharField):
    """
    Expects a list of Strings (without spaces), which are stored as a space separated String
    """

    def from_db_value(self, value, expression, connection):
        return value.split()

    def get_prep_value(self, value):
        return ' '.join(value)

    def to_python(self, value):
        if isinstance(value, list):
            return value

        if value is None:
            return value

        return value.split()

    def value_to_string(self, obj):
        value = self.value_from_object(obj)
        return ' '.join(value)


class Task(models.Model):

    CREATE = 'CRAT'
    WAIT = 'WAIT'
    PROCESSING = 'PROC'
    DONE = 'DONE'
    STATUS_CHOICES = [
        (CREATE, 'Creating'),
        (WAIT, 'Waiting', ),
        (PROCESSING, 'Processing', ),
        (DONE, 'Done', ),
    ]

    title = models.CharField(max_length=200)
    owner = models.ForeignKey(auth.get_user_model(), on_delete=models.CASCADE, related_name='tasks')
    source = models.FileField(upload_to=source_path)
    result = models.FileField(upload_to=result_path)
    language = models.CharField(choices=workers.LANGUAGE_CHOICES, max_length=5, default=None)
    translations = ListField(max_length=100, blank=True)
    status = models.CharField(choices=STATUS_CHOICES, max_length=4, default=CREATE)

    def save(self, *args, **kwargs):
        if self._state.adding:
            self.result.save('name', base.ContentFile(b''), save=False)
        super().save(*args, **kwargs)
        if self.status == self.WAIT:
            t = threading.Thread(target=utils.run_workers, kwargs={'task': self})
            t.start()



    def get_translations(self):
        return workers.TRANSLATION_CHOICES[self.language]

import os
from pathlib import Path
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

def log_path(instance, filename):
    return instance.owner.username + f'/log_{instance.title}.zip'

def edit_resource_path(instance, filename):
    return f'{instance.owner.username}/{instance.title}/resources_{instance.title}.zip'


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

    language = models.CharField(choices=workers.LANGUAGE_CHOICES, max_length=5, default=None)
    translations = ListField(max_length=100, blank=True)
    status = models.CharField(choices=STATUS_CHOICES, max_length=4, default=CREATE)

    #NOTE Collects the resources required for transcript correction, for simplified download
    edit_resources = models.FileField(upload_to=edit_resource_path)

    def save(self, *args, **kwargs):
        if self._state.adding:
            self.edit_resources.save('name', base.ContentFile(b''), save=False)
        super().save(*args, **kwargs)
        if self.status == self.WAIT:
            t = threading.Thread(target=utils.run_workers, kwargs={'task': self})
            t.start()

    def get_translations(self):
        return workers.TRANSLATION_CHOICES[self.language]


def subtask_source_path(instance, filename):
    ext = Path(filename).suffix
    return Path(instance.task.owner.username)/instance.task.title/instance.title/f'source{ext}'

def subtask_result_path(instance, filename):
    return Path(instance.task.owner.username)/instance.task.title/instance.title/'result.zip'

def subtask_log_path(instance, filename):
    return Path(instance.task.owner.username)/instance.task.title/instance.title/'log.zip'

def subtask_correction_path(instance, filename):
    ext = Path(filename).suffix
    return Path(instance.task.owner.username)/instance.task.title/instance.title/f'correction{ext}'

class SubTask(models.Model):

    title = models.CharField(max_length=200)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='subtask')
    source = models.FileField(upload_to=subtask_source_path)
    result = models.FileField(upload_to=subtask_result_path)
    log = models.FileField(upload_to=subtask_log_path)
    correction = models.FileField(upload_to=subtask_correction_path)
    finished = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['title', 'task'], name='unique_st'),
        ]

    def save(self, *args, **kwargs):
        if self._state.adding:
            self.result.save('name', base.ContentFile(b''), save=False)
            self.log.save('name', base.ContentFile(b''), save=False)
            #self.correction.save('name', base.ContentFile(b''), save=False)
        super().save(*args, **kwargs)
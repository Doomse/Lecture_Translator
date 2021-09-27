from django.core import exceptions
from django.db import models
from django.contrib import auth
from . import utils


def source_path(instance, filename):
    return instance.owner.username + '/' + filename

def result_path(instance, filename):
    return instance.owner.username + '/result.zip'


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

    title = models.CharField(max_length=200)
    owner = models.ForeignKey(auth.get_user_model(), on_delete=models.CASCADE, related_name='tasks')
    source = models.FileField(upload_to=source_path)
    result = models.FileField(upload_to=result_path, null=True, blank=True)
    language = models.CharField(choices=utils.LANGUAGE_CHOICES, max_length=10, default=None)
    translations = ListField(max_length=50, blank=True)

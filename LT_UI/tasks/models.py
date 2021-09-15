from django.db import models
from django.contrib import auth


def source_path(instance, filename):
    return instance.owner.username + '/' + filename


def transcript_path(instance, filename):
    return instance.owner.username + '/' + filename


def translation_path(instance, filename):
    return instance.owner.username + '/' + filename


class Task(models.Model):

    title = models.CharField(max_length=200)
    owner = models.ForeignKey(auth.get_user_model(), on_delete=models.CASCADE, related_name='tasks')
    source = models.FileField(upload_to=source_path)
    transcript = models.FileField(upload_to=transcript_path, blank=True, null=True)
    translation = models.FileField(upload_to=translation_path, blank=True, null=True)

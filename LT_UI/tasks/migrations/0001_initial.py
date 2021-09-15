# Generated by Django 3.2.7 on 2021-09-06 17:01

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import tasks.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('source', models.FileField(upload_to=tasks.models.source_path)),
                ('transcript', models.FileField(blank=True, null=True, upload_to=tasks.models.transcript_path)),
                ('translation', models.FileField(blank=True, null=True, upload_to=tasks.models.translation_path)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tasks', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]

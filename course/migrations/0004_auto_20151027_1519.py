# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0003_assignment'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='student',
            name='label',
        ),
        migrations.AddField(
            model_name='student',
            name='first_name',
            field=models.CharField(max_length=255, blank=True),
        ),
        migrations.AddField(
            model_name='student',
            name='last_name',
            field=models.CharField(max_length=255, blank=True),
        ),
    ]

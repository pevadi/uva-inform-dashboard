# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('storage', '0005_auto_20151102_1223'),
        ('stats', '0010_ignoredobject'),
    ]

    operations = [
        migrations.AddField(
            model_name='singleeventvariable',
            name='extensions',
            field=models.ManyToManyField(to='storage.ActivityExtension'),
        ),
    ]

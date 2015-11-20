# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stats', '0011_singleeventvariable_extensions'),
    ]

    operations = [
        migrations.AlterField(
            model_name='singleeventvariable',
            name='extensions',
            field=models.ManyToManyField(to='storage.ActivityExtension', blank=True),
        ),
    ]

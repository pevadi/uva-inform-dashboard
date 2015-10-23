# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stats', '0003_remove_valuebin_stddev'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='prediction',
            name='input_variable',
        ),
        migrations.RemoveField(
            model_name='prediction',
            name='output_variable',
        ),
        migrations.DeleteModel(
            name='Prediction',
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stats', '0005_auto_20151023_1611'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='statistic',
            name='group',
        ),
        migrations.RemoveField(
            model_name='statistic',
            name='value_bin',
        ),
        migrations.RemoveField(
            model_name='statistic',
            name='variable',
        ),
        migrations.RemoveField(
            model_name='valuebin',
            name='variable',
        ),
        migrations.DeleteModel(
            name='Statistic',
        ),
        migrations.DeleteModel(
            name='ValueBin',
        ),
    ]

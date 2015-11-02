# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('storage', '0005_auto_20151102_1223'),
    ]

    operations = [
        migrations.AddField(
            model_name='activity',
            name='value_max',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='activity',
            name='value_min',
            field=models.FloatField(null=True),
        ),
    ]

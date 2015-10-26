# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stats', '0004_auto_20151026_0810'),
    ]

    operations = [
        migrations.AddField(
            model_name='variable',
            name='axis_label',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
    ]

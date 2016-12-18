# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0004_auto_20151027_1519'),
    ]

    operations = [
        migrations.AddField(
            model_name='assignment',
            name='weight',
            field=models.DecimalField(null=True, max_digits=10, decimal_places=9, blank=True),
        ),
    ]

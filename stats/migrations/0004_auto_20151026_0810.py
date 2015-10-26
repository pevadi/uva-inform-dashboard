# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stats', '0003_auto_20151026_0553'),
    ]

    operations = [
        migrations.AlterField(
            model_name='variable',
            name='type',
            field=models.CharField(default=b'IN', max_length=3, choices=[(b'IN', b'Input variable'), (b'OUT', b'Output variable'), (b'I/O', b'Both input and output variable')]),
        ),
    ]

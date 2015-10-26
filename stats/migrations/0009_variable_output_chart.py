# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stats', '0008_auto_20151026_1334'),
    ]

    operations = [
        migrations.AddField(
            model_name='variable',
            name='output_chart',
            field=models.CharField(default=b'NON', max_length=3, choices=[(b'NON', b'No output chart'), (b'GSS', b'Gauss plot'), (b'PIE', b'Pie chart')]),
        ),
    ]

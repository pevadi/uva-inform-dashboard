# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stats', '0005_variable_axis_label'),
    ]

    operations = [
        migrations.AddField(
            model_name='variable',
            name='post_processing',
            field=models.CharField(default=b'NON', max_length=3, choices=[(b'S2M', b'Convert from seconds to minutes'), (b'S2H', b'Convert from seconds to hours'), (b'NON', b"Don't perform post processing")]),
        ),
    ]

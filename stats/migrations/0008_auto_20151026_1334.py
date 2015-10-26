# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stats', '0007_variable_order'),
    ]

    operations = [
        migrations.AlterField(
            model_name='variable',
            name='post_processing',
            field=models.CharField(default=b'NON', max_length=3, choices=[(b'S2M', b'Convert from seconds to minutes'), (b'S2H', b'Convert from seconds to hours'), (b'5.5', b'Convert to boolean whether bigger than 5.5'), (b'NON', b"Don't perform post processing")]),
        ),
    ]

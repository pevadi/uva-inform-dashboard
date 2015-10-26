# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stats', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AssignmentLinkedVariable',
            fields=[
                ('singleeventvariable_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='stats.SingleEventVariable')),
                ('compare_method', models.CharField(default=b'A', max_length=1, choices=[(b'A', b'Hours after assignment was made available.'), (b'B', b'Hours before the assignment was due.')])),
            ],
            options={
                'abstract': False,
            },
            bases=('stats.singleeventvariable',),
        ),
    ]

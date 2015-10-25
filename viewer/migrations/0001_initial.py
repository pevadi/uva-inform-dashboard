# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='GroupAssignment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('group', models.CharField(max_length=1, choices=[(b'A', b'Dashboard'), (b'B', b'No dashboard')])),
                ('student', models.CharField(max_length=255)),
                ('datetime', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('storage', '0004_activity_remotely_stored'),
    ]

    operations = [
        migrations.CreateModel(
            name='ActivityExtension',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('key', models.URLField(max_length=255)),
                ('value', models.CharField(max_length=255)),
                ('location', models.CharField(default=b'R', max_length=2, choices=[(b'R', b'Result extension')])),
            ],
        ),
        migrations.AddField(
            model_name='activity',
            name='extensions',
            field=models.ManyToManyField(to='storage.ActivityExtension'),
        ),
    ]

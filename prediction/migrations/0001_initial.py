# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Prediction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('input_value', models.FloatField()),
                ('output_value', models.FloatField()),
                ('probability', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='PredictionVariable',
            fields=[
                ('name', models.CharField(max_length=100, serialize=False, primary_key=True)),
                ('label', models.CharField(max_length=255, null=True, blank=True)),
                ('type', models.CharField(default=b'IN', max_length=3, choices=[(b'IN', b'Input variable'), (b'OUT', b'Output variable')])),
            ],
        ),
        migrations.CreateModel(
            name='PredictionVariableValue',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.FloatField()),
                ('variable', models.ForeignKey(related_name='values', to='prediction.PredictionVariable')),
            ],
        ),
        migrations.AddField(
            model_name='prediction',
            name='input_variable',
            field=models.ForeignKey(related_name='+', to='prediction.PredictionVariable'),
        ),
        migrations.AddField(
            model_name='prediction',
            name='output_variable',
            field=models.ForeignKey(related_name='+', to='prediction.PredictionVariable'),
        ),
    ]

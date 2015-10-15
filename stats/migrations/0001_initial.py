# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0001_initial'),
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
            name='Statistic',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('student', models.CharField(max_length=255)),
                ('value', models.FloatField()),
                ('datetime', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='StatisticGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=50)),
                ('label', models.CharField(max_length=255, blank=True)),
                ('members', models.ManyToManyField(to='course.Student', blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Variable',
            fields=[
                ('name', models.CharField(max_length=100, serialize=False, primary_key=True)),
                ('label', models.CharField(max_length=255, blank=True)),
                ('type', models.CharField(default=b'IN', max_length=3, choices=[(b'IN', b'Input variable'), (b'OUT', b'Output variable')])),
            ],
        ),
        migrations.CreateModel(
            name='VariableValue',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.FloatField()),
                ('variable', models.ForeignKey(related_name='values', to='stats.Variable')),
            ],
        ),
        migrations.AddField(
            model_name='statistic',
            name='group',
            field=models.ForeignKey(to='stats.StatisticGroup'),
        ),
        migrations.AddField(
            model_name='statistic',
            name='variable',
            field=models.ForeignKey(related_name='+', to='stats.Variable'),
        ),
        migrations.AddField(
            model_name='prediction',
            name='input_variable',
            field=models.ForeignKey(related_name='+', to='stats.Variable'),
        ),
        migrations.AddField(
            model_name='prediction',
            name='output_variable',
            field=models.ForeignKey(related_name='+', to='stats.Variable'),
        ),
    ]

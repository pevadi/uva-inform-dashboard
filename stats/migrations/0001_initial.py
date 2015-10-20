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
                ('group', models.ForeignKey(to='course.CourseGroup', blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='ValueBin',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('lower', models.FloatField()),
                ('upper', models.FloatField()),
                ('count', models.PositiveSmallIntegerField(null=True, blank=True)),
                ('mean', models.FloatField(null=True, blank=True)),
                ('stddev', models.FloatField(null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='ValueHistory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('student', models.CharField(max_length=255)),
                ('value', models.FloatField()),
                ('datetime', models.DateTimeField(auto_now_add=True)),
                ('group', models.ForeignKey(to='course.CourseGroup')),
            ],
        ),
        migrations.CreateModel(
            name='Variable',
            fields=[
                ('name', models.CharField(max_length=100, serialize=False, primary_key=True, blank=True)),
                ('label', models.CharField(max_length=255, blank=True)),
                ('num_bins', models.PositiveSmallIntegerField(default=10, blank=True)),
                ('last_consumed_activity_pk', models.PositiveIntegerField(null=True, blank=True)),
                ('type', models.CharField(default=b'IN', max_length=3, choices=[(b'IN', b'Input variable'), (b'OUT', b'Output variable')])),
            ],
        ),
        migrations.CreateModel(
            name='AvgGradeVariable',
            fields=[
                ('variable_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='stats.Variable')),
            ],
            bases=('stats.variable',),
        ),
        migrations.AddField(
            model_name='variable',
            name='course',
            field=models.ForeignKey(to='course.Course'),
        ),
        migrations.AddField(
            model_name='valuehistory',
            name='variable',
            field=models.ForeignKey(related_name='+', to='stats.Variable'),
        ),
        migrations.AddField(
            model_name='valuebin',
            name='variable',
            field=models.ForeignKey(related_name='+', to='stats.Variable'),
        ),
        migrations.AddField(
            model_name='statistic',
            name='value_bin',
            field=models.ForeignKey(to='stats.ValueBin', blank=True),
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

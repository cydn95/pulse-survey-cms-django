# -*- coding: utf-8 -*-
# Generated by Django 1.11.25 on 2020-01-09 14:31
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('survey', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ConceptClass',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('conceptClassName', models.CharField(max_length=50)),
                ('childOf', models.PositiveIntegerField()),
                ('conceptClassDesc', models.TextField()),
                ('conceptClassIRI', models.TextField()),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='survey.Project')),
            ],
        ),
        migrations.CreateModel(
            name='ConceptInstance',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('instanceName', models.CharField(max_length=100)),
                ('instanceIRI', models.TextField()),
                ('instanceDesc', models.TextField()),
                ('preferLabel', models.CharField(blank=True, max_length=100)),
                ('conceptClass', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='setting.ConceptClass')),
            ],
        ),
        migrations.CreateModel(
            name='ControlType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('controlTypeName', models.CharField(max_length=50)),
            ],
        ),
    ]

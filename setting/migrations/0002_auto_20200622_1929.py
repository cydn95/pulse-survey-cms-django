# -*- coding: utf-8 -*-
# Generated by Django 1.11.25 on 2020-06-23 02:29
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('setting', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='conceptclass',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='survey.Project'),
        ),
        migrations.AlterField(
            model_name='conceptinstance',
            name='conceptClass',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='setting.ConceptClass'),
        ),
    ]

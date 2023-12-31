# -*- coding: utf-8 -*-
# Generated by Django 1.11.25 on 2020-05-25 08:52
from __future__ import unicode_literals

import colorfield.fields
from django.db import migrations, models
import tinymce.models


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0007_nikelmobilepage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='nikelmobilepage',
            name='backgroundColor',
            field=colorfield.fields.ColorField(blank=True, default='#FF0000', max_length=18),
        ),
        migrations.AlterField(
            model_name='nikelmobilepage',
            name='pageContent',
            field=tinymce.models.HTMLField(blank=True),
        ),
        migrations.AlterField(
            model_name='nikelmobilepage',
            name='pageText',
            field=models.CharField(blank=True, max_length=500),
        ),
    ]

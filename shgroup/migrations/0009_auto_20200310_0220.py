# -*- coding: utf-8 -*-
# Generated by Django 1.11.25 on 2020-03-10 09:20
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shgroup', '0008_auto_20200309_1333'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shcategory',
            name='icon',
            field=models.FileField(blank=True, upload_to='uploads/shcategory'),
        ),
    ]

# -*- coding: utf-8 -*-
# Generated by Django 1.11.25 on 2020-04-09 02:50
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organization', '0003_auto_20200318_0233'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organization',
            name='name',
            field=models.CharField(blank=True, max_length=200, verbose_name='Organization'),
        ),
        migrations.AlterField(
            model_name='useravatar',
            name='name',
            field=models.ImageField(blank=True, upload_to='uploads/user', verbose_name='Avatar'),
        ),
        migrations.AlterField(
            model_name='userteam',
            name='name',
            field=models.CharField(blank=True, max_length=50, verbose_name='Department'),
        ),
        migrations.AlterField(
            model_name='usertitle',
            name='name',
            field=models.CharField(blank=True, max_length=50, verbose_name='Job Title'),
        ),
    ]

# -*- coding: utf-8 -*-
# Generated by Django 1.11.25 on 2020-06-10 21:14
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0011_auto_20200604_0310'),
    ]

    operations = [
        migrations.CreateModel(
            name='ToolTipGuide',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=50)),
                ('content', models.CharField(blank=True, max_length=1000)),
                ('img', models.FileField(blank=True, upload_to='uploads/tooltip')),
            ],
        ),
        migrations.AddField(
            model_name='nikelmobilepage',
            name='img',
            field=models.FileField(blank=True, upload_to='uploads/nikel'),
        ),
    ]

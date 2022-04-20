# -*- coding: utf-8 -*-
# Generated by Django 1.11.25 on 2020-06-17 20:31
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shgroup', '0026_remove_projectuser_project'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shcategory',
            name='survey',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='survey.Survey'),
        ),
        migrations.AlterField(
            model_name='shgroup',
            name='survey',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='survey.Survey'),
        ),
        migrations.AlterField(
            model_name='shmapping',
            name='projectUser',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='projectUser', to='shgroup.ProjectUser'),
        ),
        migrations.AlterField(
            model_name='shmapping',
            name='shCategory',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shgroup.SHCategory'),
        ),
        migrations.AlterField(
            model_name='shmapping',
            name='subProjectUser',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subProjectUser', to='shgroup.ProjectUser'),
        ),
    ]

# -*- coding: utf-8 -*-
# Generated by Django 1.11.25 on 2019-11-09 16:42
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('survey', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('team', '0001_initial'),
        ('auth', '0008_alter_user_username_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='MapType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='ProjectUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='survey.Project')),
            ],
        ),
        migrations.CreateModel(
            name='SHCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('SHCategoryName', models.CharField(blank=True, max_length=50)),
                ('SHCategoryDesc', models.CharField(blank=True, max_length=200)),
                ('colour', models.CharField(blank=True, max_length=50)),
                ('icon', models.CharField(blank=True, max_length=100)),
                ('mapType', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='shgroup.MapType')),
            ],
        ),
        migrations.CreateModel(
            name='SHGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('SHGroupName', models.CharField(max_length=255)),
                ('SHGroupAbbrev', models.CharField(blank=True, max_length=50)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='survey.Project')),
            ],
        ),
        migrations.CreateModel(
            name='SHMapping',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('relationshipStatus', models.CharField(blank=True, max_length=100)),
                ('project', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.PROTECT, to='survey.Project')),
                ('projectUser', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.PROTECT, to='shgroup.ProjectUser')),
                ('shCategory', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.PROTECT, to='shgroup.SHCategory')),
                ('subjectUser', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.PROTECT, related_name='subjectUser', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='shcategory',
            name='shGroup',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.PROTECT, to='shgroup.SHGroup'),
        ),
        migrations.AddField(
            model_name='shcategory',
            name='survey',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='survey.Survey'),
        ),
        migrations.AddField(
            model_name='projectuser',
            name='shGroup',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='shgroup.SHGroup'),
        ),
        migrations.AddField(
            model_name='projectuser',
            name='team',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='team.Team'),
        ),
        migrations.AddField(
            model_name='projectuser',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='projectuser',
            name='userPermission',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='auth.Permission'),
        ),
    ]

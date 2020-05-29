import os
from pathlib import Path
from email.mime.image import MIMEImage
from django.contrib.postgres.fields import JSONField
from django.db import models
from survey.models import Project, Survey
from django.contrib.auth.models import User
from django.contrib.auth.models import Permission
from team.models import Team
#from gremlin import addVertex
from django.forms.models import ModelForm
from django.forms.widgets import CheckboxSelectMultiple
from django import forms
from rest_framework.authtoken.models import Token
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import get_template, render_to_string
from django.conf import settings
from django.contrib import messages

# Create your models here.

class SHGroup(models.Model):
    SHGroupName = models.CharField(max_length=255)
    SHGroupAbbrev = models.CharField(max_length=50, blank=True)
    # project = models.ForeignKey(Project, on_delete=models.PROTECT)
    survey = models.ForeignKey(Survey, on_delete=models.PROTECT)

    def __str__(self):
        return self.SHGroupName

class MapType(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name
        
class SHCategory(models.Model):
    survey = models.ForeignKey(Survey, on_delete=models.PROTECT)
    # shGroup = models.ForeignKey(SHGroup, on_delete=models.PROTECT, blank=True)
    SHCategoryName = models.CharField(max_length=50, blank=True)
    SHCategoryDesc = models.CharField(max_length=200, blank=True)
    mapType = models.ForeignKey(MapType, on_delete=models.PROTECT)
    colour = models.CharField(max_length=50, blank=True)
    # icon = models.CharField(max_length=255, blank=True)
    icon = models.FileField(upload_to='uploads/shcategory', blank=True)
    
    def __str__(self):
        return self.SHCategoryName

class ProjectUser(models.Model):
    project = models.ForeignKey(Project, on_delete=models.PROTECT)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    projectUserTitle = models.CharField(max_length=50, blank=True, verbose_name='Project Title', help_text='Role / Title of the stakeholder on this Project')
    # projectUserRoleDesc = models.CharField(max_length=500, blank=True, verbose_name='Description')
    #userPermission = models.ManyToManyField(Permission, blank=True)
    # team = models.ForeignKey(Team, on_delete=models.PROTECT)
    team = models.ForeignKey(Team, null=True, blank=True, verbose_name='Project Team')
    #shCategory = models.ForeignKey(SHCategory, null=True, blank=True)
    shGroup = models.ForeignKey(SHGroup, null=True, blank=True, verbose_name='SHGroup')

    # class Meta:
    #     unique_together = ['project', 'user']

    def __str__(self):
        return '{0} - {1}'.format(self.project, self.user.username)

    def save(self, *args, **kwargs):
        super(ProjectUser, self).save(*args, **kwargs)

        # temporary hold
        # project = Project.objects.get(id=self.project.id)
        # user = User.objects.get(id=self.user.id)
        # token = Token.objects.get(user_id=self.user.id)

        # image_path_logo = os.path.join(settings.STATIC_ROOT, 'email', 'img', 'logo-2.png')
        # image_name_logo = Path(image_path_logo).name
        # image_path_container = os.path.join(settings.STATIC_ROOT, 'email', 'img', 'container.png')
        # image_name_container = Path(image_path_container).name
        # image_path_connect = os.path.join(settings.STATIC_ROOT, 'email', 'img', 'connect.png')
        # image_name_connect = Path(image_path_connect).name

        # subject = 'Welcome to Pulse'
        # message = get_template('email.html').render(
        #     {
        #         'project_name': project,
        #         'image_name_logo': image_name_logo,
        #         'image_name_container': image_name_container,
        #         'image_name_connect': image_name_connect,
        #         'token': token.key,
        #         'email': user.email,
        #         'first_name': user.first_name,
        #         'last_name': user.last_name,
        #         'site_url': settings.SITE_URL
        #     }
        # )
        # email_from = settings.DEFAULT_FROM_EMAIL
        # recipient_list = [user.email,]

        # email = EmailMultiAlternatives(subject=subject, body=message, from_email=email_from, to=recipient_list)
        # email.attach_alternative(message, "text/html")
        # email.content_subtype = 'html'
        # email.mixed_subtype = 'related'

        # with open(image_path_logo, mode='rb') as f_logo:
        #     image_logo = MIMEImage(f_logo.read())
        #     email.attach(image_logo)
        #     image_logo.add_header('Content-ID', f"<{image_name_logo}>")

        # with open(image_path_connect, mode='rb') as f_connect:
        #     image_connect = MIMEImage(f_connect.read())
        #     email.attach(image_connect)
        #     image_connect.add_header('Content-ID', f"<{image_name_connect}>")

        # email.send()

# class ProjectUserForm(ModelForm):
#     userPermission = forms.ModelMultipleChoiceField(queryset=Permission.objects.all(), required=False)

class SHMapping(models.Model):
    shCategory = models.ForeignKey(SHCategory, on_delete=models.PROTECT)
    projectUser = models.ForeignKey(ProjectUser, on_delete=models.PROTECT, related_name='projectUser')
    subProjectUser = models.ForeignKey(ProjectUser, on_delete=models.PROTECT, related_name='subProjectUser')
    relationshipStatus = models.CharField(max_length=100, blank=True)

    class Meta:
        unique_together = ['shCategory', 'projectUser', 'subProjectUser']
        
    def __str__(self):
        return '{0} - {1} - {2}'.format(self.shCategory, self.projectUser, self.subProjectUser)

class MyMapLayout(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, blank=False)
    projectUser = models.ManyToManyField(ProjectUser, blank=True)
    layout_json = JSONField(default=dict, blank=True)

    # class Meta:
    #     unique_together = ['user', 'project',]


class ProjectMapLayout(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, blank=False)
    projectUser = models.ManyToManyField(ProjectUser, blank=True)
    layout_json = JSONField(default=dict, blank=True)

    # class Meta:
    #     unique_together = ['user', 'project',]
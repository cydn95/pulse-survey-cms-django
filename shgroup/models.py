from django.contrib.postgres.fields import JSONField
from django.db import models
from survey.models import Project, Survey
from django.contrib.auth.models import User
from django.contrib.auth.models import Permission
from team.models import Team
from gremlin import addVertex
from django.forms.models import ModelForm
from django.forms.widgets import CheckboxSelectMultiple
from django import forms

# Create your models here.
class SHGroup(models.Model):
    SHGroupName = models.CharField(max_length=255)
    SHGroupAbbrev = models.CharField(max_length=50, blank=True)
    project = models.ForeignKey(Project, on_delete=models.PROTECT)

    def __str__(self):
        return self.SHGroupName

    def save(self, *args, **kwargs):
        super(SHGroup, self).save(*args, **kwargs)
        print(self.SHGroupName)

        if self.id is not None:
            data = [{
                'id': 'stakeholder-{0}'.format(self.id),
                'label': 'stakeholder_{0}'.format(self.id),
                'type': 'stakeholder',
                'text': self.SHGroupName
            }]
            print(data)
            ret = addVertex(data)
            print(ret)

class ProjectUser(models.Model):
    project = models.ForeignKey(Project, on_delete=models.PROTECT)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    userPermission = models.ManyToManyField(Permission, blank=True)
    team = models.ForeignKey(Team, on_delete=models.PROTECT)
    shGroup = models.ForeignKey(SHGroup, on_delete=models.PROTECT)

    def __str__(self):
        return '{0} - {1}'.format(self.user.username, self.project)

    def save(self, *args, **kwargs):
        super(ProjectUser, self).save(*args, **kwargs)
        print(self.project)

        print(self.user)
        if self.id is not None:
            data = [{
                'id': 'user-{0}'.format(self.id),
                'label': 'user_{0}'.format(self.id),
                'type': 'user',
                'text': '{0}'.format(self.user)
            }]
            print(data)
            ret = addVertex(data)
            print(ret)

class ProjectUserForm(ModelForm):
    userPermission = forms.ModelMultipleChoiceField(queryset=Permission.objects.all(), required=False)

class MapType(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class SHCategory(models.Model):
    survey = models.ForeignKey(Survey, on_delete=models.PROTECT)
    shGroup = models.ForeignKey(SHGroup, on_delete=models.PROTECT, blank=True)
    SHCategoryName = models.CharField(max_length=50, blank=True)
    SHCategoryDesc = models.CharField(max_length=200, blank=True)
    mapType = models.ForeignKey(MapType, on_delete=models.PROTECT)
    colour = models.CharField(max_length=50, blank=True)
    icon = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.SHCategoryName

    def save(self, *args, **kwargs):
        super(SHCategory, self).save(*args, **kwargs)
        print(self.SHCategoryName)

        if self.id is not None:
            data = [{
                'id': 'category-{0}'.format(self.id),
                'label': 'category_{0}'.format(self.id),
                'type': 'category',
                'text': self.SHCategoryName
            }]
            print(data)
            ret = addVertex(data)
            print(ret)

class SHMapping(models.Model):
    projectUser = models.ForeignKey(ProjectUser, on_delete=models.PROTECT, blank=True)
    subjectUser = models.ForeignKey(User, on_delete=models.PROTECT, related_name="subjectUser", blank=True)
    project = models.ForeignKey(Project, on_delete=models.PROTECT, blank=True)
    shCategory = models.ForeignKey(SHCategory, on_delete=models.PROTECT, blank=True)
    relationshipStatus = models.CharField(max_length=100, blank=True)


class MyMapLayout(models.Model):
    projectUser = models.ForeignKey(ProjectUser, on_delete=models.PROTECT, blank=False)
    project = models.ForeignKey(Project, on_delete=models.PROTECT, blank=False)
    layout_json = JSONField(default=dict)

    class Meta:
        unique_together = ('projectUser', 'project',)


class ProjectMapLayout(models.Model):
    projectUser = models.ForeignKey(ProjectUser, on_delete=models.PROTECT, blank=False)
    project = models.ForeignKey(Project, on_delete=models.PROTECT, blank=False)
    layout_json = JSONField(default=dict)

    class Meta:
        unique_together = ('projectUser', 'project',)
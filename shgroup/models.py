from django.db import models
from survey.models import Project, Survey
from django.contrib.auth.models import User
from django.contrib.auth.models import Permission
from team.models import Team
# If you use a custom user model you should use:
# from django.contrib.auth import get_user_model
# User = get_user_model()

# Create your models here.
class SHGroup(models.Model):
    SHGroupName = models.CharField(max_length=255)
    SHGroupAbbrev = models.CharField(max_length=50, blank=True)
    project = models.ForeignKey(Project, on_delete=models.PROTECT)

    def __str__(self):
        return self.SHGroupName

class ProjectUser(models.Model):
    project = models.ForeignKey(Project, on_delete=models.PROTECT)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    userPermission = models.ForeignKey(Permission, on_delete=models.PROTECT)
    team = models.ForeignKey(Team, on_delete=models.PROTECT)
    shGroup = models.ForeignKey(SHGroup, on_delete=models.PROTECT)

class SHGroupUser(models.Model):
    shGroup = models.ForeignKey(SHGroup, on_delete=models.PROTECT)
    #user = models.ForeignKey(User, on_delete=models.PROTECT)
    projectUser = models.ForeignKey(ProjectUser, on_delete=models.PROTECT)

class SHCategory(models.Model):
    survey = models.ForeignKey(Survey, on_delete=models.PROTECT)
    shGroup = models.ForeignKey(SHGroup, on_delete=models.PROTECT, blank=True)
    SHCategoryName = models.CharField(max_length=50, blank=True)
    SHCategoryDesc = models.CharField(max_length=200, blank=True)
    mapType = models.CharField(max_length=50, blank=True)
    colour = models.CharField(max_length=50, blank=True)
    icon = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.SHCategoryName

class SHMapping(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="user", blank=True)
    subjectUser = models.ForeignKey(User, on_delete=models.PROTECT, related_name="subjectUser", blank=True)
    project = models.ForeignKey(Project, on_delete=models.PROTECT, blank=True)
    shCategory = models.ForeignKey(SHCategory, on_delete=models.PROTECT, blank=True)
    relationshipStatus = models.CharField(max_length=100, blank=True)
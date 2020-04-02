from django.db import models
#from organization.models import Organization
#from gremlin import addVertex
from survey.models import Project

# Create your models here.
class Team(models.Model):
    name = models.CharField(max_length=200)
    # organization = models.CharField(max_length=200)
    project = models.ForeignKey(Project, on_delete=models.PROTECT)

    def __str__(self):
        return self.name



    
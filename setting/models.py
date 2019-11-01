from django.db import models
from survey.models import Project

# Create your models here.
class ControlType(models.Model):
    controlTypeName = models.CharField(max_length=50)

    def __str__(self):
        return self.controlTypeName

class ConceptClass(models.Model):
    project = models.ForeignKey(Project, on_delete=models.PROTECT)
    conceptClassName = models.CharField(max_length=50)
    childOf = models.PositiveIntegerField()
    conceptClassDesc = models.TextField()
    conceptClassIRI = models.TextField()

    def __str__(self):
        return self.conceptClassName

class ConceptInstance(models.Model):
    instanceName = models.CharField(max_length=100)
    conceptClass = models.ForeignKey(ConceptClass, on_delete=models.PROTECT)
    instanceIRI = models.TextField()
    instanceDesc = models.TextField()
    preferLabel = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.instanceName
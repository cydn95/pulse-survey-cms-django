from django.db import models
#from gremlin import addVertex
from tinymce.models import HTMLField
from rgbfield.fields import RGBColorField
from colorfield.fields import ColorField

class Client(models.Model):
    clientName = models.CharField(max_length=200)

    def __str__(self):
        return self.clientName

class Project(models.Model):
    client = models.ForeignKey(Client, on_delete=models.PROTECT)
    projectName = models.CharField(max_length=200)

    def __str__(self):
        return self.projectName
    
class Survey(models.Model):
    project = models.ForeignKey(Project, on_delete=models.PROTECT)
    surveyTitle = models.CharField(max_length=200)

    def __str__(self):
        return self.surveyTitle

class ConfigPage(models.Model):
    # project = models.ForeignKey(Project, on_delete=models.PROTECT)
    survey = models.ForeignKey(Survey, on_delete=models.PROTECT)
    tabName = models.CharField(max_length=40)
    pageName = models.CharField(max_length=200)
    pageContent = HTMLField()

    def __str__(self):
        return self.pageName

class NikelMobilePage(models.Model):
    # project = models.ForeignKey(Project, on_delete=models.PROTECT)
    survey = models.ForeignKey(Survey, on_delete=models.PROTECT)
    pageName = models.CharField(max_length=50)
    pageText = models.CharField(max_length=500, blank=True)
    backgroundColor = ColorField(default="#FF0000", blank=True)
    pageContent = HTMLField()
    pageOrder = models.PositiveIntegerField(default=0, blank=False, null=False, verbose_name='Page Order')
    img = models.FileField(upload_to='uploads/nikel', blank=True)

    class Meta(object):
        ordering = ['pageOrder']

    def __str__(self):
        return self.pageName

class ToolTipGuide(models.Model):
    title = models.CharField(max_length=50)
    content = models.CharField(max_length=1000, blank=True)
    img = models.FileField(upload_to='uploads/tooltip', blank=True)

    def __str__(self):
        return self.title
        
class Driver(models.Model):
    driverName = models.CharField(max_length=200)
    iconPath = models.CharField(max_length=255, blank=True)
    driveOrder = models.PositiveIntegerField(default=0, blank=False, null=False)
    survey = models.ForeignKey(Survey, on_delete=models.PROTECT)
    
    class Meta(object):
        ordering = ['driveOrder']

    def __str__(self):
        return self.driverName

class ProjectVideoUpload(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    project = models.ForeignKey(Project, on_delete=models.PROTECT)
    videoFile = models.FileField(upload_to='uploads/pvideo')

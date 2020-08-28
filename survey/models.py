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
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    projectName = models.CharField(max_length=200)

    def __str__(self):
        return self.projectName
    
class Survey(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    surveyTitle = models.CharField(max_length=200)
    isStandard = models.BooleanField(default=False)
    isActive = models.BooleanField(default=False)
    customGroup1 = models.CharField(max_length=100, blank=True, default="")
    customGroup2 = models.CharField(max_length=100, blank=True, default="")
    customGroup3 = models.CharField(max_length=100, blank=True, default="")

    def __str__(self):
        return self.surveyTitle

    def save(self, *args, **kwargs):
        current_survey = Survey.objects.filter(project_id=self.project_id, isActive=True)
        if current_survey.count() == 0:
            self.isActive = True
        super(Survey, self).save(*args, **kwargs)

class ConfigPage(models.Model):
    # project = models.ForeignKey(Project, on_delete=models.CASCADE)
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
    tabName = models.CharField(max_length=40)
    pageName = models.CharField(max_length=200)
    pageContent = HTMLField()

    def __str__(self):
        return self.pageName

class NikelMobilePage(models.Model):
    # project = models.ForeignKey(Project, on_delete=models.CASCADE)
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
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
    place = models.CharField(max_length=50)
    title = models.CharField(max_length=50)
    content = models.CharField(max_length=1000)
    img = models.FileField(upload_to='uploads/tooltip', blank=True)
    group = models.CharField(max_length=50)
    tooltipOrder = models.PositiveIntegerField(default=0, blank=False, null=False, verbose_name='Tooltip Order')

    class Meta(object):
        ordering = ['tooltipOrder']
        
    def __str__(self):
        return self.title

class Driver(models.Model):
    driverName = models.CharField(max_length=200)
    iconPath = models.CharField(max_length=255, blank=True)
    driveOrder = models.PositiveIntegerField(default=0, blank=False, null=False)
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
    isStandard = models.BooleanField(default=False)
    
    class Meta(object):
        ordering = ['driveOrder']

    def __str__(self):
        return self.driverName

class ProjectVideoUpload(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    videoFile = models.FileField(upload_to='uploads/pvideo')

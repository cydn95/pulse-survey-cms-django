from django.db import models
#from gremlin import addVertex

class Client(models.Model):
    clientName = models.CharField(max_length=200)

    def __str__(self):
        return self.clientName

class Project(models.Model):
    #client = models.ForeignKey(Client, on_delete=models.PROTECT)
    projectName = models.CharField(max_length=200)

    def __str__(self):
        return self.projectName

    # def save(self, *args, **kwargs):
    #     super(Project, self).save(*args, **kwargs)
    #     #print(self.projectName)

    #     if self.id is not None:
    #         data = [{
    #             'id': 'project-{0}'.format(self.id),
    #             'label': 'project_{0}'.format(self.id),
    #             'type': 'project',
    #             'text': self.projectName
    #         }]
    #         #print(data)
    #         ret = addVertex(data)
    #         #print(ret)

class Survey(models.Model):
    project = models.ForeignKey(Project, on_delete=models.PROTECT)
    surveyTitle = models.CharField(max_length=200)

    def __str__(self):
        return self.surveyTitle

class Driver(models.Model):
    driverName = models.CharField(max_length=200)
    iconPath = models.CharField(max_length=255, blank=True)
    driveOrder = models.PositiveIntegerField(default=0, blank=False, null=False)

    class Meta(object):
        ordering = ['driveOrder']

    def __str__(self):
        return self.driverName

class ProjectVideoUpload(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    project = models.ForeignKey(Project, on_delete=models.PROTECT)
    videoFile = models.FileField(upload_to='uploads/pvideo')

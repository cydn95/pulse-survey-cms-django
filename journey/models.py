from django.db import models

# Create your models here.
class Journey(models.Model):
    pageName = models.CharField(max_length=50)
    pageLink = models.URLField(max_length=255)
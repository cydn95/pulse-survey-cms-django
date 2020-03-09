from django.db import models
from rgbfield.fields import RGBColorField

# Create your models here.
class Journey(models.Model):
    pageName = models.CharField(max_length=50)
    pageLink = models.URLField(max_length=255)
    xPos = models.IntegerField()
    yPos = models.IntegerField()
    color = RGBColorField(default="#afd8f8")
    orderId = models.PositiveIntegerField()
    

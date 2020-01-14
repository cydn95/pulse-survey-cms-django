from django.db import models
from django.contrib.auth.models import User
from gremlin import addVertex


# Create your models here.
class Organization(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super(Organization, self).save(*args, **kwargs)
        #print(self.name)

        if self.id is not None:
            data = [{
                'id': 'organization-{0}'.format(self.id),
                'label': 'organization_{0}'.format(self.id),
                'type': 'organization',
                'text': self.name
            }]
            #print(data)
            ret = addVertex(data)
            #print(ret)

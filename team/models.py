from django.db import models
from organization.models import Organization
from gremlin import addVertex

# Create your models here.
class Team(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT)
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super(Team, self).save(*args, **kwargs)
        print(self.name)

        if self.id is not None:
            data = [{
                'id': 'team-{0}'.format(self.id),
                'label': 'team_{0}'.format(self.id),
                'type': 'team',
                'text': self.name
            }]
            print(data)
            ret = addVertex(data)
            print(ret)

    
from django.db import models

class Hero(models.Model):
    api_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=100, unique=True)
    intelligence = models.IntegerField()
    strength = models.IntegerField()
    speed = models.IntegerField()
    power = models.IntegerField()

    def __str__(self):
        return self.name
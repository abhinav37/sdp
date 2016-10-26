from __future__ import unicode_literals

from django.db import models

# Create your models here.

class User(models.Model):
	username = models.CharField(max_length=8)
	password = models.CharField(max_length=10)
	name = models.CharField(max_length=40)
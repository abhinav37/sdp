from __future__ import unicode_literals
from django.contrib.auth.models import User

from django.db import models
import datetime

# Create your models here.

class Instructor(models.Model):
	instructor = models.OneToOneField(
        User,
        primary_key=True,
    )
	def __str__(self):
		return self.instructor.first_name + " " + self.instructor.last_name 

class Category(models.Model):
	name = models.CharField(max_length=40)
	def __str__(self):
		return self.name

class Course(models.Model):
	category = models.ForeignKey(Category)
	instructor = models.ForeignKey(Instructor)
	name = models.CharField(max_length=40)
	description = models.TextField()
	deployed = models.IntegerField(default=0)
	def __str__(self):
		return self.name

class Module(models.Model):
	course = models.ForeignKey(Course, on_delete=models.CASCADE)
	name = models.CharField(max_length=40)
	position = models.IntegerField(default=0)
	def __str__(self):
		return self.name

def fileUploadPath(instance, filename):
    return '{0}/{1}/{2}'.format(instance.course.id, instance.module.id, filename)

class Component(models.Model):
	course = models.ForeignKey(Course, on_delete=models.CASCADE)
	module = models.ForeignKey(Module)
	name = models.CharField(max_length=40)
	file = models.FileField(upload_to=fileUploadPath, null=True, blank=True, default = None)
	position = models.IntegerField(default=0)
	def __str__(self):
		return self.name
	
class Participant(models.Model):
	participant = models.OneToOneField(
        User,
        primary_key=True,
    )
	course = models.ForeignKey(Course, null=True, blank=True, default = None)
	access = models.IntegerField(default=0)
	def __str__(self):
		return self.participant.first_name + " " + self.participant.last_name 

class HR(models.Model):
	hr_id = models.IntegerField(default=0)


class History(models.Model):
	course = models.ForeignKey(Course, on_delete=models.CASCADE)
	participant = models.ForeignKey(Participant)
	dateCompleted = models.DateField(default=datetime.date.today)	

from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver

@receiver(pre_delete, sender=Component)
def component_delete(sender, instance, **kwargs):
    # Pass false so FileField doesn't save the model.
    instance.file.delete(False)
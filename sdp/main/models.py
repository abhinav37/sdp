from __future__ import unicode_literals
from django.contrib.auth.models import User
from embed_video.fields import EmbedVideoField

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
	
	def getCourses(self):
		return Course.objects.filter(instructor=self)

	def createCourse(self):
		newCourse = Course(name="New Course", description="Add a description for your course", deployed=0, category_id=-1, instructor=self)
		newCourse.save()
		return newCourse

class Category(models.Model):
	name = models.CharField(max_length=40)
	def __str__(self):
		return self.name

	def getCourses(self):
		return Course.objects.filter(category=self)
	
	def rename(self, name):
		self.name = name
		self.save()

class Course(models.Model):
	category = models.ForeignKey(Category)
	instructor = models.ForeignKey(Instructor)
	name = models.CharField(max_length=40)
	description = models.TextField()
	deployed = models.IntegerField(default=0)
	def __str__(self):
		return self.name

	def getModuleCount(self):
		return self.getModules().count()

	def getModules(self):
		return Module.objects.filter(course = self)

	def getComponents(self):
		return Component.objects.filter(course = self)

	def addModule(self, moduleName, modulePosition):
		new_module = Module(name = moduleName, position = modulePosition, course = self)
		new_module.save()

	def getParticipants(self):
		return Participant.objects.filter(course = self)

	def toggleDeployed(self):
		self.deployed = 1 - self.deployed
		self.save()

class Module(models.Model):
	course = models.ForeignKey(Course, on_delete=models.CASCADE)
	name = models.CharField(max_length=40)
	position = models.IntegerField(default=0)
	def __str__(self):
		return self.name

	def getComponents(self):
		return Component.objects.filter(course=self.course, module=self)
	
	def addComponent(self, componentName, componentPosition, compType):
		if compType == 'video':
			newComponent = VideoComponent(name = componentName, position = componentPosition, course = self.course, module = self, video="https://www.youtube.com/watch?v=dQw4w9WgXcQ")
			newComponent.save()
		else:
			newComponent = FileComponent(name = componentName, position = componentPosition, course = self.course, module = self)
			newComponent.save()

def fileUploadPath(instance, filename):
    return '{0}/{1}/{2}/{3}'.format(instance.course.id, instance.module.id, instance.id, filename)

class Component(models.Model):
	course = models.ForeignKey(Course, on_delete=models.CASCADE)
	module = models.ForeignKey(Module)
	name = models.CharField(max_length=40)
	position = models.IntegerField(default=0)
	def __str__(self):
		return self.name

class FileComponent(Component):
	file = models.FileField(upload_to=fileUploadPath, null=True, blank=True, default = None)
	
class VideoComponent(Component):
	video = EmbedVideoField()

class Participant(models.Model):
	participant = models.OneToOneField(
        User,
        primary_key=True,
    )
	course = models.ForeignKey(Course, null=True, blank=True, default = None)
	access = models.IntegerField(default=0)
	def __str__(self):
		return self.participant.first_name + " " + self.participant.last_name
	
	def getEnrolledCourse(self):
		return self.course

	def enroll(self, course):
		self.course = course 
		self.access = 1
		self.save()

	def dropCurrentCourse(self):
		self.course = None
		self.access = 0
		self.save()
	
	def getCompletedCourses(self):
		return History.objects.filter(participant=self)

class HR(models.Model):
	hr_id = models.IntegerField(default=0)


class History(models.Model):
	course = models.ForeignKey(Course, on_delete=models.CASCADE)
	participant = models.ForeignKey(Participant)
	dateCompleted = models.DateField(default=datetime.date.today)

	def updateDate(self, date):
		self.dateCompleted = date 
		self.save()

from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver

@receiver(pre_delete, sender=Component)
def component_delete(sender, instance, **kwargs):
     # Pass false so FileField doesn't save the model.
	try:
		instance.filecomponent.file.delete(False)
	except FileComponent.DoesNotExist:
		pass




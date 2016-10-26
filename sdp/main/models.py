from __future__ import unicode_literals

from django.db import models

# Create your models here.

class User(models.Model):
	username = models.CharField(max_length=8)
	password = models.CharField(max_length=10)
	name = models.CharField(max_length=40)
	
class Instructor(models.Model):
	instructor = models.OneToOneField(
        User,
        primary_key=True,
    )

class Category(models.Model):
	name = models.CharField(max_length=40)

class Course(models.Model):
	category = models.ForeignKey(Category)
	instructor = models.ForeignKey(Instructor)
	name = models.CharField(max_length=40)
	description = models.TextField()
	deployed = models.IntegerField(default=0)

class Module(models.Model):
	course = models.ForeignKey(Course)
	name = models.CharField(max_length=40)
	position = models.IntegerField(default=0)

class Component(models.Model):
	course = models.ForeignKey(Course)
	module = models.ForeignKey(Module)
	name = models.CharField(max_length=40)
	filename = models.CharField(max_length=40)
	position = models.IntegerField(default=0)
	
class Participant(models.Model):
	participant = models.OneToOneField(
        User,
        primary_key=True,
    )
	course = models.ForeignKey(Course)
	most_recent_unlocked = models.IntegerField(default=0)
	

	


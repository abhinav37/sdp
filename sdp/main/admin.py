from django.contrib import admin

from .models import Instructor 
from .models import Category 
from .models import Course
from .models import Module 
from .models import Participant 

admin.site.register(Instructor)
admin.site.register(Category)
admin.site.register(Course)
admin.site.register(Module)
admin.site.register(Participant)




# Register your models here.

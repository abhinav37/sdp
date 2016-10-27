from django.contrib import admin

from .models import User
from .models import Instructor 
from .models import Category 
from .models import Course
from .models import Module 
from .models import Component
from .models import Participant 

admin.site.register(User)
admin.site.register(Instructor)
admin.site.register(Category)
admin.site.register(Course)
admin.site.register(Module)
admin.site.register(Component)
admin.site.register(Participant)




# Register your models here.

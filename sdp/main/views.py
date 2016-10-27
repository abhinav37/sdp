from django.http import HttpResponse
from .models import User
from django.template import loader
from .models import Course, Category, Participant, Module, Component


def index(request):
	try:
		return HttpResponse(request.POST['enrolflag'])
	except Exception,e:
		return HttpResponse("404 Not found"); 

def participant(request):
	all_courses = Course.objects.all()
	template = loader.get_template('main/participant.html')
	context = {'all_courses': all_courses, }
 	return HttpResponse(template.render(context,request))

def instructor(request):
 	try:
 		print(request.POST['courseName'])
		newCourse = Course.objects.all().order_by("id").reverse()[0]
		newCourse.name = request.POST['courseName']
		newCourse.description = request.POST['courseDesc']
		newCourse.category_id=request.POST['category']
		newCourse.instructor_id=1
		newCourse.save()
	except Exception, e:
		pass
	finally:
		course_list = Course.objects.filter(instructor_id=1)
		template = loader.get_template('main/instructor.html')
		context = {'course_list': course_list}
		return HttpResponse(template.render(context,request))

def newCourse(request):
	newCourse = Course(name="New Course", description="Add a description for your course", deployed=0, category_id=1, instructor_id=1)
	newCourse.save()

	category_list = Category.objects.all()
	course_id = Course.objects.all().order_by("id").reverse()[0].id
	module_list = Module.objects.filter(course_id=course_id).order_by("position")
	
	template = loader.get_template('main/new.html')
	context = {'categories': category_list, 'modules': module_list, 'course_id': course_id }
 	return HttpResponse(template.render(context,request))

def view_course(request,course_id):
	course_details = Course.objects.filter(id=course_id)[0]
	template=loader.get_template('main/courseInfo.html')
	context={'information': course_details }
	return HttpResponse(template.render(context,request))

def enrolling(request):
	participantObj = Participant.objects.filter(pk=1)[0]
	participantObj.course_id = request.POST['course_id']
	participantObj.save()
	return HttpResponse("You have been enrolled in this course!")

def loadComponents(request):
	component_list = Component.objects.filter(module_id=request.POST['module_id'], course_id=request.POST['course_id']).order_by("position")
	context = {'components': component_list, 'module_id': request.POST['module_id']}
	template = loader.get_template('main/component.html')
	return HttpResponse(template.render(context,request))

def add_module(request):
	course_id = Course.objects.all().order_by("id").reverse()[0].id
	module_list = Module.objects.filter(course_id=course_id).order_by("position")
	mods = Module.objects.filter(course_id=course_id)
	if not mods:
		module_position = 0
	else:
		module_position = mods.order_by("position").reverse()[0].position

	courseObj = Course.objects.filter(pk=course_id)[0]
	new_module = Module(name=request.POST['module_name'], position = module_position+1, course = courseObj)
	new_module.save()

	#calling the newCourse funciton again
	
	module_list = Module.objects.filter(course_id=course_id).order_by("position")
	
	template = loader.get_template('main/module.html')
	context = {'modules': module_list}
 	return HttpResponse(template.render(context,request))

def add_component(request):

	comps = Component.objects.filter(course_id=request.POST['course_id'], module_id=request.POST['module_id'])
	if not comps:
		component_position = 0
	else:
		component_position = comps.order_by("position").reverse()[0].position

	courseObj = Course.objects.filter(pk=request.POST['course_id'])[0]
	moduleObj = Module.objects.filter(pk=request.POST['module_id'])[0]
	new_component =Component(name=request.POST['component_name'], filename="xxx.xxx", position=component_position, course=courseObj, module=moduleObj)
	new_component.save()

	
	component_list = Component.objects.filter(course_id=request.POST['course_id'], module_id=request.POST['module_id']).order_by("position")
	
	template = loader.get_template('main/component.html')
	context = {'components': component_list}
 	return HttpResponse(template.render(context,request))
	

	


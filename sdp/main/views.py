from django.http import HttpResponse
from .models import User
from django.template import loader
from .models import Course, Category, Participant, Module, Component, Instructor
from django.shortcuts import redirect
import json

def index(request):
	try:
		return HttpResponse(request.POST['enrolflag'])
	except Exception,e:
		return HttpResponse("404 Not found"); 

def participant(request):
	#TODO use participant id of logged in user
	participantID = 3
	participantObj = Participant.objects.filter(pk=participantID)[0]
	template = loader.get_template('main/participant.html')

	if participantObj.course_id is not None:
		allCourses = Course.objects.exclude(pk=participantObj.course_id)
		enrolledCourse = Course.objects.filter(pk=participantObj.course_id)[0]
		context = {'enrolledCourse': enrolledCourse, 'allCourses': allCourses, }
	else:
		allCourses = Course.objects.all()
		context = {'allCourses': allCourses, }
	return HttpResponse(template.render(context,request))

def instructor(request):
 	try:
		if request.POST['modulePositions'] != "":
			mods = json.loads(request.POST['modulePositions'])
			for idx,mod in enumerate(mods):
				module = Module.objects.filter(pk=mod)[0]
				module.position = idx+1
				module.save()

		if request.POST['compsPositions'] != "":
			comps = json.loads(request.POST['compsPositions'])
			print comps
			for key, value in comps.iteritems():
				for idx,comp in enumerate(value):
					compo = Component.objects.filter(pk=int(comp))[0]
					compo.position = idx+1
					compo.save()

		newCourse = Course.objects.filter(pk=request.POST['course_id'])[0]
		newCourse.name = request.POST['courseName']
		newCourse.description = request.POST['courseDesc']
		newCourse.category_id = request.POST['category']
		#TODO intructor id based on login
		newCourse.instructor_id=1
		newCourse.save()
	except Exception, e:
		print e
		pass
	finally:
		#TODO intructor id based on login
		course_list = Course.objects.filter(instructor_id=1)
		template = loader.get_template('main/instructor.html')
		context = {'course_list': course_list}
		return HttpResponse(template.render(context,request))

def newCourse(request):
	#TODO change category id, intructor id, deployed implementation
	newCourse = Course(name="New Course", description="Add a description for your course", deployed=0, category_id=1, instructor_id=1)
	newCourse.save()

	category_list = Category.objects.all()
	course_id = Course.objects.all().order_by("id").reverse()[0].id
	module_list = Module.objects.filter(course_id=course_id).order_by("position")
	
	template = loader.get_template('main/new.html')
	context = {'categories': category_list, 'modules': module_list, 'course_id': course_id }
 	return HttpResponse(template.render(context,request))

def view_course(request,course_id):
	#TODO get logged in participant id
	participantID = 3
	participantObj = Participant.objects.filter(pk=participantID)[0]
	template=loader.get_template('main/courseInfo.html')

	if participantObj.course_id is None:
		#not enrolled in any course, show everything + option to enroll
		courseDetails = Course.objects.filter(id=course_id)[0]
		moduleList = Module.objects.filter(course_id=course_id).order_by("position")
		x = 3
	else:
		if participantObj.course_id == int(course_id):
			#load course accordingly, as this is Participant's enrolled course
			courseDetails = Course.objects.filter(id=course_id)[0]
			moduleList = Module.objects.filter(course_id=course_id).order_by("position")
			x = 1
		else:
			#load course accordingly, Participant is enrolled in another course. give option to drop current course to get this course
			courseDetails = Course.objects.filter(id=course_id)[0]
			moduleList = Module.objects.filter(course_id=course_id).order_by("position")
			x = 2

	context={'courseDetails': courseDetails, 'moduleList': moduleList, 'enrollStatus': x }
	return HttpResponse(template.render(context,request))

def addDrop(request):
	#TODO get logged in participant id
	participantID = 3
	participantObj = Participant.objects.filter(pk=participantID)[0]
	if request.POST['drop'] == "1":
		participantObj.course_id = None
	else:
		participantObj.course_id = request.POST['course_id']
	participantObj.save()
	return redirect(participant)

def loadComponents(request):
	component_list = Component.objects.filter(module_id=request.POST['module_id'], course_id=request.POST['course_id']).order_by("position")
	context = {'components': component_list, 'module_id': request.POST['module_id']}
	template = loader.get_template('main/componentList.html')
	return HttpResponse(template.render(context,request))

def loadComponentBody(request):
	compFile = request.FILES.get('compFile', False)
	compName = request.POST.get('compName', False)
	componentObj = Component.objects.filter(pk=request.POST['component_id'])[0]
	if compFile:
		#TODO delete old file if exits
		componentObj.file = compFile
		componentObj.save()
	
	if compName:
		componentObj.name = compName
		componentObj.save()

	context = {'component': componentObj}
	template = loader.get_template('main/componentBody.html')
	return HttpResponse(template.render(context,request))

def add_module(request):
	course_id = request.POST['course_id']
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
	new_component =Component(name=request.POST['component_name'], file=None, position=component_position+1, course=courseObj, module=moduleObj)
	new_component.save()

	component_list = Component.objects.filter(course_id=request.POST['course_id'], module_id=request.POST['module_id']).order_by("position")
	
	template = loader.get_template('main/componentList.html')
	context = {'components': component_list}
 	return HttpResponse(template.render(context,request))

def editCourse(request, course_id):
	courseObj = Course.objects.filter(pk=course_id)[0]
	modules = Module.objects.filter(course_id=course_id).order_by("position")
	components = Component.objects.filter(course_id=course_id).order_by("position")
	category_list = Category.objects.all()

	template = loader.get_template('main/editCourse.html')
	context = {'course': courseObj,'modules': modules ,'components': components, 'categories': category_list}

 	return HttpResponse(template.render(context,request))

def admin(request):		
	template = loader.get_template('main/admin.html')
	all_categories = Category.objects.all()
	all_users = User.objects.all()
	all_instructor= Instructor.objects.filter()
	print(all_instructor)
	context = {'all_categories': all_categories,'all_users': all_users,'all_instructor':all_instructor }
	return HttpResponse(template.render(context,request))
	
def adminchange(request):
    info=request.POST['info']
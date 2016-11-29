from django.http import HttpResponse
from django.template import loader
from .models import Course, Category, Participant, Module, Component, Instructor, HR, History
from django.shortcuts import redirect

from django.contrib.auth.models import User
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required, user_passes_test

import json

#######Tests for users#######
def isInstructor(user):
    return user.is_staff==1

def isAdmin(user):
	return user.is_superuser
#############################

def isHR(user):
	ishr = HR.objects.filter(hr_id=user_id)
	if ishr:
		return True
	else:
		return False

def index(request):
	if request.user.is_authenticated:
		return redirect('participant')
	else:
		return redirect('login') 

def logOut(request):
	if request.user.is_authenticated:
		logout(request)
	return redirect('login') 


@login_required
def participant(request):
	#TODO use participant id of logged in user
	participantID = request.user.id
	participantObj = Participant.objects.filter(pk=participantID)[0]
	template = loader.get_template('main/participant.html')

	if participantObj.course_id is not None:
		allCourses = Course.objects.filter(deployed=1).exclude(pk=participantObj.course_id)
		enrolledCourse = Course.objects.filter(pk=participantObj.course_id)[0]
		context = {'enrolledCourse': enrolledCourse, 'allCourses': allCourses, }
	else:
		allCourses = Course.objects.filter(deployed=1)
		context = {'allCourses': allCourses, }
	return HttpResponse(template.render(context,request))

@login_required
@user_passes_test(isInstructor)
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
		newCourse.instructor_id = request.user.id
		newCourse.save()
	except Exception, e:
		print e
		pass
	finally:
		#TODO intructor id based on login
		course_list = Course.objects.filter(instructor_id=request.user.id)
		template = loader.get_template('main/instructor.html')
		context = {'course_list': course_list}
		return HttpResponse(template.render(context,request))

@login_required
@user_passes_test(isInstructor)
def newCourse(request):
	#TODO deployed implementation
	newCourse = Course(name="New Course", description="Add a description for your course", deployed=0, category_id=-1, instructor_id=request.user.id)
	newCourse.save()

	category_list = Category.objects.all()
	course_id = Course.objects.all().order_by("id").reverse()[0].id
	module_list = Module.objects.filter(course_id=course_id).order_by("position")
	
	template = loader.get_template('main/new.html')
	context = {'categories': category_list, 'modules': module_list, 'course_id': course_id }
 	return HttpResponse(template.render(context,request))

@login_required
@user_passes_test(isInstructor)
def deployCourse(request):
	participants = Participant.objects.filter(course_id = request.POST['course_id'])
	print participants
	if not participants:
		course = Course.objects.filter(pk=request.POST['course_id'])[0]
		course.deployed = 1 - course.deployed
		course.save()
	 	return HttpResponse("Success")
	else:
		return HttpResponse("Fail")

@login_required
def view_course(request,course_id):
	participantID = request.user.id
	participantObj = Participant.objects.filter(pk=participantID)[0]
	template=loader.get_template('main/courseInfo.html')
	course = Course.objects.filter(id=course_id)[0]
	lastModule = Module.objects.filter(course_id=course_id).last().id
	
	if participantObj.course_id is None:
		#not enrolled in any course, show everything + option to enroll
		modules = Module.objects.filter(course_id=course_id).order_by("position")
		x = 3
	else:
		if participantObj.course_id == int(course_id):
			#load course accordingly, as this is Participant's enrolled course
			lastUnlocked = participantObj.access
			modules = Module.objects.filter(course_id=course_id, position__lte = lastUnlocked).order_by("position")
			x = 1
		else:
			#load course accordingly, Participant is enrolled in another course. give option to drop current course to get this course
			modules = Module.objects.filter(course_id=course_id).order_by("position")
			x = 2

	context={'course': course, 'modules': modules, 'enrollStatus': x, 'participant_id': participantID, 'lastModule': lastModule }
	return HttpResponse(template.render(context,request))

def completeCourse(request, course_id, participant_id):
	modCount = Module.objects.filter(course_id=course_id).count()
	participantObj = Participant.objects.filter(pk=participant_id)[0]
	if participantObj.access == modCount:
		courseObj = Course.objects.filter(pk=course_id)[0]
		history = History(course=courseObj, participant=participantObj)
		history.save()
		participantObj.course_id = None
		participantObj.access = 0
		participantObj.save()
	
	return redirect(participant)

@login_required
def loadModules(request, course_id):
	participantID = request.user.id
	participantObj = Participant.objects.filter(pk=participantID)[0]
	lastUnlocked = participantObj.access
	modules = Module.objects.filter(course_id=course_id, position__lte = lastUnlocked).order_by("position")
	
	template = loader.get_template('main/module.html')
	context = {'modules': modules}
 	return HttpResponse(template.render(context,request))

@login_required
def addDrop(request):
	participantID = request.user.id
	participantObj = Participant.objects.filter(pk=participantID)[0]
	if request.POST['drop'] == "1":
		participantObj.course_id = None
		participantObj.access = 0
	else:
		participantObj.course_id = request.POST['course_id']
		participantObj.access = 1
	participantObj.save()
	return redirect(participant)

@login_required															
def loadComponents(request):
	participantID = request.POST.get('participant_id', False)
	moduleID = request.POST['module_id']
	courseID = request.POST['course_id']
	modList = Module.objects.filter(course_id=courseID).order_by("position")
	lastModule = modList.last().id
	canAdd = 1
	if participantID:
		participantObj = Participant.objects.filter(pk=participantID)[0]
		access = participantObj.access
		noOfMods = modList.count()
		accessibleMod = modList[access-1].id
		if accessibleMod == int(moduleID):
			if access < noOfMods:
				participantObj.access = access + 1
				participantObj.save()
		canAdd = 0
		print lastModule

	component_list = Component.objects.filter(module_id=moduleID, course_id=courseID).order_by("position")
	context = {'components': component_list, 'module_id': moduleID, 'canAdd': canAdd , 'lastModule': lastModule }
	template = loader.get_template('main/componentList.html')
	return HttpResponse(template.render(context,request))

@login_required
def loadComponentBody(request):
	compFile = request.FILES.get('compFile', False)
	compName = request.POST.get('compName', False)
	componentObj = Component.objects.filter(pk=request.POST['component_id'])[0]
	if compFile:
		#TODO delete old file if exists
		componentObj.file = compFile
		componentObj.save()
	
	if compName:
		componentObj.name = compName
		componentObj.save()

	context = {'component': componentObj}
	template = loader.get_template('main/componentBody.html')
	return HttpResponse(template.render(context,request))

@login_required
def partiComponentBody(request, course_id):
	componentObj = Component.objects.filter(pk=request.POST['component_id'])[0]
	context = {'component': componentObj}
	template = loader.get_template('main/partiComponentBody.html')
	return HttpResponse(template.render(context,request))

@login_required
@user_passes_test(isInstructor)
def renameModule(request):
	course_id = request.POST['course_id']
	moduleToChange = Module.objects.filter(pk=request.POST['module_id'])[0]
	moduleToChange.name = request.POST['module_name']
	moduleToChange.save()

	module_list = Module.objects.filter(course_id=course_id).order_by("position")	
	template = loader.get_template('main/module.html')
	context = {'modules': module_list}
 	return HttpResponse(template.render(context,request))

@login_required
@user_passes_test(isInstructor)
def deleteModule(request):
	course_id = request.POST['course_id']
	moduleToDelete = Module.objects.filter(pk=request.POST['module_id'])[0]
	moduleToDelete.delete()

	module_list = Module.objects.filter(course_id=course_id).order_by("position")	
	template = loader.get_template('main/module.html')
	context = {'modules': module_list}
 	return HttpResponse(template.render(context,request))

@login_required
@user_passes_test(isInstructor)
def addModule(request):
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

	module_list = Module.objects.filter(course_id=course_id).order_by("position")	
	template = loader.get_template('main/module.html')
	context = {'modules': module_list}
 	return HttpResponse(template.render(context,request))

@login_required
@user_passes_test(isInstructor)
def deleteComponent(request):
	course_id = request.POST['course_id']
	compToDelete = Component.objects.filter(pk=request.POST['component_id'])[0]
	compToDelete.delete()

	component_list = Component.objects.filter(course_id=request.POST['course_id'], module_id=request.POST['module_id']).order_by("position")
	template = loader.get_template('main/componentList.html')
	context = {'components': component_list, 'canAdd': 1}
 	return HttpResponse(template.render(context,request))

@login_required
@user_passes_test(isInstructor)
def addComponent(request):
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
	context = {'components': component_list, 'canAdd': 1}
 	return HttpResponse(template.render(context,request))

@login_required
@user_passes_test(isInstructor)
def editCourse(request, course_id):
	courseObj = Course.objects.filter(pk=course_id)[0]
	modules = Module.objects.filter(course_id=course_id).order_by("position")
	components = Component.objects.filter(course_id=course_id).order_by("position")
	category_list = Category.objects.all()

	template = loader.get_template('main/editCourse.html')
	context = {'course': courseObj,'modules': modules ,'components': components, 'categories': category_list}
 	return HttpResponse(template.render(context,request))

@login_required
@user_passes_test(isAdmin)
def admin(request):		
	template = loader.get_template('main/admin.html')
	all_categories = Category.objects.all()
	all_users = User.objects.all()
	all_instructor= Instructor.objects.filter()
	
	context = {'all_categories': all_categories,'all_users': all_users,'all_instructor':all_instructor }
	return HttpResponse(template.render(context,request))

@login_required
@user_passes_test(isAdmin)
def deleteCategory(request):
	try:
		if request.POST['category_id']:
			x = Category.objects.filter(id=request.POST['category_id'])
			if not Course.objects.filter(category=x):
				Category.objects.filter(id=request.POST['category_id']).delete()
				print "yes del"		
				return HttpResponse("del")
			else:
				print "no del"
				return HttpResponse("no")
		else:
			
			return HttpResponse("no")
	except Exception, e:
		return HttpResponse("ex")
		print e
		pass

@login_required
@user_passes_test(isAdmin)
def adminchange(request): 
	try:
		if request.POST['val']=='2':
			
			us=User.objects.filter(id=request.POST['u_id'])
			x = Instructor.objects.filter(instructor=us)
			if not Course.objects.filter(instructor=x):
				us=User.objects.filter(id=request.POST['u_id'])[0]
				Instructor.objects.filter(instructor_id=us.id).delete()
				print "deleted"
				return HttpResponse("change")
			else:
				print "has course"
				return HttpResponse("no")
		elif request.POST['val']=='1':
				us=User.objects.filter(id=request.POST['u_id'])[0]
				x = Instructor(us.id)
				x.save()
				return HttpResponse("done")
		
	
	except Exception, e:
		print e
		return HttpResponse("expetion")
		pass

@login_required
@user_passes_test(isAdmin)
def newCategory(request):
	try:
		if request.POST['cat']:
			newCat=Category(name=request.POST['cat'])
			newCat.save()
			return HttpResponse(newCat.id)
		else:
			return HttpResponse("exist")
	except Exception, e:
		print e
		pass

def register(request):
	return callReg(request, {})

def callReg(request, context1):
	template = loader.get_template('main/register.html')
	return HttpResponse(template.render(context1, request))

def regComplete(request):
	uname = request.POST['username']
	fname = request.POST['fname']
	lname = request.POST['lname']
	try:
		userObjs = User.objects.get(username=uname)
		context = {'error': 1, 'username': uname, 'fname': fname, 'lname': lname, }
		return callReg(request, context)
	except Exception, e:
		newUser = User.objects.create_user(uname, None, request.POST['pwd']) 
		newUser.first_name = fname
		newUser.last_name = lname
		newUser.is_staff = 0	
		newUser.save()

		newParti = Participant(pk=newUser.id)
		newParti.save()
		#TODO redirect to login page
		return redirect('login')


def participantList(request):
	template = loader.get_template('main/hr.html')
	all_users = User.objects.all()
	context = {'all_users' : all_users}
	return HttpResponse(template.render(context,request))


def courseHistory(request, participant_id):	
	template = loader.get_template('main/courseHistory.html')
	courseHistory = History.objects.filter(participant=participant_id)
	participantObj = Participant.objects.filter(pk = participant_id)
	context = {'courseHistory': courseHistory, 'participantObj': participantObj[0]}
	return HttpResponse(template.render(context,request))

from django.http import HttpResponse
from django.template import loader
from .models import Course, Category, Participant, Module, Component, Instructor, HR, History, VideoComponent, FileComponent
from django.shortcuts import redirect

from django.contrib.auth.models import User
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required, user_passes_test

import json,datetime

############## User Functions ##############
def isInstructor(user):
    return user.is_staff==1

def isAdmin(user):
	return user.is_superuser

def isHR(user):
	ishr = HR.objects.filter(hr_id=user.id)
	if ishr:
		return True
	else:
		return False

def getUsers():
	return User.objects.all()

############## Index Views ##############

def index(request):
	if request.user.is_authenticated:
		return redirect('participant')
	else:
		return redirect('login')  

@login_required
def participant(request):
	participantObj = Participant.objects.filter(pk=request.user.id)[0]
	courseHistory = participantObj.getCompletedCourses()
	
	courseList = {}
	categories = Category.objects.all()
	for category in categories:
		courses = category.getCourses().filter(deployed=1).exclude(pk=participantObj.course_id)
		if courses:
			courseList[category] = courses
	
	context = {'enrolledCourse': participantObj.getEnrolledCourse(), 'courseList': courseList, 'courseHistory':courseHistory }	
	template = loader.get_template('main/participant.html')
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
			for key, value in comps.iteritems():
				for idx,comp in enumerate(value):
					compo = Component.objects.filter(pk=int(comp))[0]
					compo.position = idx+1
					compo.save()

		newCourse = Course.objects.filter(pk=request.POST['course_id'])[0]
		newCourse.name = request.POST['courseName']
		newCourse.description = request.POST['courseDesc']
		newCourse.category_id = request.POST['category']
		newCourse.instructor_id = request.user.id
		newCourse.save()
	except Exception, e:
		print e
		pass
	finally:
		instructorObj = Instructor.objects.get(pk=request.user.id)
		courseDelete = Course.objects.filter(category_id=-1)
		for course in courseDelete:
			course.delete()
		course_list = instructorObj.getCourses()

		template = loader.get_template('main/instructor.html')
		context = {'course_list': course_list}
		return HttpResponse(template.render(context,request))

############## Course Views ##############

@login_required
@user_passes_test(isInstructor)
def newCourse(request):
	instructorObj = Instructor.objects.get(pk=request.user.id)
	courseObj = instructorObj.createCourse()
	category_list = Category.objects.all()

	template = loader.get_template('main/new.html')
	context = {'categories': category_list, 'course': courseObj }
 	return HttpResponse(template.render(context,request))

@login_required
@user_passes_test(isInstructor)
def editCourse(request, course_id):
	courseObj = Course.objects.get(pk=course_id)
	modules = courseObj.getModules().order_by("position")
	components = courseObj.getComponents().order_by("position")
	category_list = Category.objects.all()

	template = loader.get_template('main/new.html')
	context = {'course': courseObj, 'modules': modules, 'components': components, 'categories': category_list, 'edit': 1}
 	return HttpResponse(template.render(context,request))

@login_required
@user_passes_test(isInstructor)
def deployCourse(request):
	courseObj = Course.objects.get(pk=request.POST['course_id'])
	participants = courseObj.getParticipants()
	if not participants:
		courseObj.toggleDeployed()
	 	return HttpResponse("Success")
	else:
		return HttpResponse("Fail")

@login_required
def view_course(request,course_id):
	participantObj = Participant.objects.get(pk=request.user.id)
	courseObj = Course.objects.get(pk=course_id)
	x = courseObj.getModules()

	modules = courseObj.getModules().order_by("position")
	if participantObj.getEnrolledCourse() is None:
		x = 3 #not enrolled in any course, show everything + option to enroll
	else:
		if participantObj.course_id == int(course_id):
			#load course accordingly, as this is Participant's enrolled course
			modules = modules.filter(position__lte = participantObj.access)
			x = 1
		else:
			#load course accordingly, Participant is enrolled in another course. give option to drop current course to get this course
			x = 2
	
	template=loader.get_template('main/courseInfo.html')
	context={'course': courseObj, 'modules': modules, 'enrollStatus': x, 'participant_id': request.user.id }
	return HttpResponse(template.render(context,request))

def viewFullContent(request,course_id):
	participantObj = Participant.objects.get(pk=request.user.id)
	courseObj = Course.objects.get(pk=course_id)
	modules = courseObj.getModules().order_by("position")
	
	if participantObj.course_id is None:
		x = 1 #not enrolled in any course, show everything + option to enroll
	else:
		if participantObj.course_id == int(course_id):
			x = 2 #load course accordingly, as this is Participant's enrolled course
		else:
			x = 3 #load course accordingly, Participant is enrolled in another course. give option to drop current course to get this course

	template=loader.get_template('main/viewFullContent.html')
	context={'course': courseObj, 'modules': modules, 'enrollStatus': x, 'participant_id': request.user.id }
	return HttpResponse(template.render(context,request))

def completeCourse(request, course_id, participant_id):
	courseObj = Course.objects.get(pk=course_id)
	modCount = courseObj.getModuleCount()
	participantObj = Participant.objects.get(pk=participant_id)
	if participantObj.access == modCount:
		courseHistory = History.objects.filter(course=courseObj, participant=participantObj)
		if courseHistory:
			courseHistory[0].updateDate(datetime.date.today())
		else:
			history = History(course=courseObj, participant=participantObj)
			history.save()
		participantObj.dropCurrentCourse()
	
	return redirect(participant)

@login_required
def addDrop(request):
	participantObj = Participant.objects.get(pk=request.user.id)
	if request.POST['drop'] == "1":
		participantObj.dropCurrentCourse()
	else:
		courseObj = Course.objects.get(pk=request.POST['course_id'])
		participantObj.enroll(courseObj)

	return redirect(participant)

############## Component Views ##############

@login_required															
def loadComponents(request):
	participantID = request.POST.get('participant_id', False)
	courseObj = Course.objects.get(pk=request.POST['course_id'])
	modList = courseObj.getModules().order_by("position")
	lastModule = modList.last().id
	canAdd = 1

	if participantID:
		participantObj = Participant.objects.get(pk=participantID)
		access = participantObj.access
		noOfMods = modList.count()
		accessibleMod = modList[access-1].id
		if accessibleMod == int(request.POST['module_id']):
			if access < noOfMods:
				participantObj.access = access + 1
				participantObj.save()
		canAdd = 0

	if request.POST.get('override', False):
		canAdd = 0
	
	moduleObj = Module.objects.get(pk=request.POST['module_id'])
	component_list = moduleObj.getComponents().order_by("position")
	context = {'components': component_list, 'module_id': request.POST['module_id'], 'canAdd': canAdd , 'lastModule': lastModule }
	print context
	template = loader.get_template('main/componentList.html')
	return HttpResponse(template.render(context,request))

@login_required
def loadComponentBody(request):
	fileType = request.POST.get('fileType', False)
	compName = request.POST.get('compName', False)
	componentObj = Component.objects.get(pk=request.POST['component_id'])

	if fileType:
		compFile = request.FILES.get('compFile', False)
		if compFile:
			#os.remove(os.path.join(settings.MEDIA_ROOT, componentObj.fileComponent.file))
			componentObj.createFile(compFile)
		else:
			compVideo = request.POST.get('compVideo', False)
			if compVideo:
				componentObj.createVideo(compVideo)
	
	if compName:
		componentObj.name = compName

	componentObj.save()
	context = {'component': componentObj}
	template = loader.get_template('main/componentBody.html')
	return HttpResponse(template.render(context,request))

@login_required
def partiComponentBody(request, course_id):
	componentObj = Component.objects.get(pk=request.POST['component_id'])
	if componentObj.videocomponent:
		context = {'component': componentObj.videocomponent}
	else:
		context = {'component': componentObj.filecomponent}

	template = loader.get_template('main/partiComponentBody.html')
	return HttpResponse(template.render(context,request))

@login_required
@user_passes_test(isInstructor)
def deleteComponent(request):
	compToDelete = Component.objects.get(pk=request.POST['component_id'])
	compToDelete.delete()
	moduleObj = Module.objects.get(pk=request.POST['module_id'])
	component_list = moduleObj.getComponents().order_by("position")

	template = loader.get_template('main/componentList.html')
	context = {'components': component_list, 'canAdd': 1}
 	return HttpResponse(template.render(context,request))

@login_required
@user_passes_test(isInstructor)
def addComponent(request):
	moduleObj = Module.objects.get(pk=request.POST['module_id'])
	comps = moduleObj.getComponents()
	if not comps:
		component_position = 0
	else:
		component_position = comps.order_by("position").reverse()[0].position
	moduleObj.addComponent(request.POST['component_name'], component_position + 1)

	component_list = moduleObj.getComponents().order_by("position")
	template = loader.get_template('main/componentList.html')
	context = {'components': component_list, 'canAdd': 1}
 	return HttpResponse(template.render(context,request))

############## Admin Views ##############

@login_required
@user_passes_test(isAdmin)
def admin(request):		
	all_categories = Category.objects.all()
	all_users = getUsers()
	all_instructor= Instructor.objects.all()
	
	template = loader.get_template('main/admin.html')
	context = {'all_categories': all_categories,'all_users': all_users,'all_instructor':all_instructor }
	return HttpResponse(template.render(context,request))

@login_required
@user_passes_test(isAdmin)
def adminchange(request): 
	try:
		if request.POST['val']=='2':
			us = User.objects.filter(id=request.POST['u_id'])
			instructorObj = Instructor.objects.filter(instructor=us)
			if instructorObj.getCourses() is None:
				us=User.objects.get(pk=request.POST['u_id'])
				us.is_staff=False
				us.save()
				Instructor.objects.get(pk=us.id).delete()
				return HttpResponse("change")
			else:
				return HttpResponse("no")
		elif request.POST['val']=='1':
				us=User.objects.get(pk=request.POST['u_id'])
				us.is_staff=True
				us.save()
				x = Instructor(us.id)
				x.save()
				return HttpResponse("done")
	except Exception, e:
		print e
		return HttpResponse("expetion")
		pass

############## Category Views ##############

@login_required
@user_passes_test(isAdmin)
def newCategory(request):
	try:
		if request.POST['cat']:
			newCat = Category(name=request.POST['cat'])
			newCat.save()
			return HttpResponse(newCat.id)
		else:
			return HttpResponse("exist")
	except Exception, e:
		print e
		pass

@login_required
@user_passes_test(isAdmin)
def deleteCategory(request):
	try:
		if request.POST['category_id']:
			x = Category.objects.filter(id=request.POST['category_id'])
			if x.getCourses() is None:
				Category.objects.get(pk=request.POST['category_id']).delete()
				return HttpResponse("del")
			else:
				return HttpResponse("no")
		else:	
			return HttpResponse("no")
	except Exception, e:
		return HttpResponse("ex")
		print e
		pass

@login_required
@user_passes_test(isAdmin)
def renameCategory(request):
	try:
		if request.POST['cat_id']:
			catObj = Category.objects.get(pk=request.POST['cat_id'])
			catObj.rename(request.POST['cat_na'])
			return HttpResponse("rnm")
		else:
			return HttpResponse("not")
	except Exception, e:
		print e
		pass

############## Login/Logout/Registration Views ##############
def callReg(request, context1):
	template = loader.get_template('main/register.html')
	return HttpResponse(template.render(context1, request))

def register(request):
	return callReg(request, {})

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
		return redirect('login')

def logOut(request):
	if request.user.is_authenticated:
		logout(request)
	return redirect('login')

def auth(request):
	username = request.POST['username']
	password = request.POST['password']
	user = authenticate(username=username, password=password)
	if user is not None:
		login(request, user)
		request.session['isHR'] = isHR(request.user)
		if not request.POST['next']:
			return redirect('participant')
		else:
			return redirect(request.POST['next'])
	else:
		form = AuthenticationForm(request)
		context = {'form' : form, 'error': "Invalid, please try again!"}
		template = loader.get_template('main/login.html')
		return HttpResponse(template.render(context,request))

############## HR Views ##############

@login_required
@user_passes_test(isHR)
def participantList(request):
	template = loader.get_template('main/hr.html')
	all_users = getUsers()
	context = {'all_users' : all_users}
	return HttpResponse(template.render(context,request))

@login_required
@user_passes_test(isHR)
def courseHistory(request, participant_id):	
	participantObj = Participant.objects.get(pk=participant_id)
	courseHistory = participantObj.getCompletedCourses() 

	context = {'courseHistory': courseHistory, 'name': participantObj }
	template = loader.get_template('main/courseHistory.html')
	return HttpResponse(template.render(context,request))

############## Module Views ##############

def loadModuleTemplate(request, module_list):
	template = loader.get_template('main/module.html')
	context = {'modules': module_list}
 	return HttpResponse(template.render(context,request))

@login_required
def loadModules(request, course_id):
	participantID = request.user.id
	participantObj = Participant.objects.filter(pk=participantID)[0]
	lastUnlocked = participantObj.access
	module_list = Module.objects.filter(course_id=course_id, position__lte = lastUnlocked).order_by("position")
	
	return loadModuleTemplate(request, module_list)

@login_required
@user_passes_test(isInstructor)
def renameModule(request):
	moduleToChange = Module.objects.filter(pk=request.POST['module_id'])[0]
	moduleToChange.name = request.POST['module_name']
	moduleToChange.save()
	courseObj = Course.objects.get(pk=request.POST['course_id'])
	module_list = courseObj.getModules().order_by("position")

	return loadModuleTemplate(request, module_list)

@login_required
@user_passes_test(isInstructor)
def deleteModule(request):
	moduleToDelete = Module.objects.filter(pk=request.POST['module_id'])[0]
	moduleToDelete.delete()
	courseObj = Course.objects.get(pk=request.POST['course_id'])
	module_list = courseObj.getModules().order_by("position")	
	
	return loadModuleTemplate(request, module_list)

@login_required
@user_passes_test(isInstructor)
def addModule(request):
	courseObj = Course.objects.get(pk=request.POST['course_id'])
	module_list = courseObj.getModules().order_by("position")
	if not module_list:
		module_position = 0
	else:
		module_position = module_list.order_by("position").reverse()[0].position
	courseObj.addModule(request.POST['module_name'], module_position + 1)
	module_list = courseObj.getModules().order_by("position")	
	
	return loadModuleTemplate(request, module_list)

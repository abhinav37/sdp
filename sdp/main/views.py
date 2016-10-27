from django.http import HttpResponse
from .models import User
from django.template import loader
from .models import Course, Category, Participant


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
 	template = loader.get_template('main/instructor.html')
 	return HttpResponse(template.render(request))

def newCourse(request):
	category_list = Category.objects.all()
	template = loader.get_template('main/new.html')
	context = {'categories': category_list }
 	return HttpResponse(template.render(context,request))

def view_course(request,course_id):
	course_details = Course.objects.filter(id=course_id)[0]
	template=loader.get_template('main/courseInfo.html')
	context={'information': course_details }
	return HttpResponse(template.render(context,request))

def enrolling(request):
	cid = Participant.objects.all(participant_id=1)
	cid.course=request.POST['enrolflag']
	cid.save()
	return HttpResponse("You have been enrolled in this course")
